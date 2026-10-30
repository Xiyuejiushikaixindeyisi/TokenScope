import errno

import pytest

from tokenscope.monitoring.ma.service import MaService
from tokenscope.monitoring.service import MonitoringService

from .helpers import binding, row, write_csv


@pytest.mark.parametrize("fault", ["disk", "header", "quote", "window", "encoding"])
def test_failures_not_partial_success(
    service: MonitoringService, monkeypatch: pytest.MonkeyPatch, fault: str
) -> None:
    write_csv(service.inputs.root / "pre.csv", [row("pre")])
    write_csv(service.inputs.root / "now.csv", [row()])
    ma = MaService(service)
    receipt = ma.submit(binding())
    if fault == "disk":

        def fail(*args: object) -> None:
            raise OSError(errno.ENOSPC, "injected full disk")

        monkeypatch.setattr(service.inputs, "snapshot", fail)
    elif fault == "header":
        (service.inputs.root / "now.csv").write_text("unknown\nx\n")
    elif fault == "quote":
        with (service.inputs.root / "now.csv").open("a") as stream:
            stream.write('"unterminated')
    elif fault == "encoding":
        (service.inputs.root / "now.csv").write_bytes(b"\xff\xfe")
    else:
        write_csv(service.inputs.root / "now.csv", [row(request_time="2026-10-20T09:00:00Z")])
    result = ma.processor.process_next()
    assert result is not None and result.state == "failed", result
    assert ma.catalog().total == "0"
    assert (
        ma.store.receipt(receipt.ma_run_id).error_code
        == {
            "disk": "STORAGE_UNAVAILABLE",
            "header": "MISSING_COLUMNS",
            "quote": "MALFORMED_CSV",
            "encoding": "MALFORMED_CSV",
            "window": "OUTSIDE_WINDOW",
        }[fault]
    )


def test_all_unassigned_is_not_empty(service: MonitoringService) -> None:
    write_csv(service.inputs.root / "pre.csv", [])
    write_csv(service.inputs.root / "now.csv", [row(instance_uuid="", request_time="bad")])
    ma = MaService(service)
    receipt = ma.submit(binding())
    result = ma.processor.process_next()
    assert result is not None and result.state == "completed"
    assert ma.catalog().entries[0].empty_scope_reason == "all_unassigned"
    issues = ma.quality(receipt.ma_run_id)
    assert any(i.field == "request_time" for i in issues.issues)


def test_exported_spec_mismatch(service: MonitoringService) -> None:
    import csv

    write_csv(service.inputs.root / "pre.csv", [])
    source = service.inputs.root / "now.csv"
    values = row() | {"model_standard_name": "different"}
    with source.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(values))
        writer.writeheader()
        writer.writerow(values)
    ma = MaService(service)
    ma.submit(binding())
    result = ma.processor.process_next()
    assert result is not None and result.error_code == "MIXED_SPEC"
