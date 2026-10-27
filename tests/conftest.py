import csv
import io
import json
from pathlib import Path

import pytest

from tokenscope.domain import DEFAULT_SETTINGS
from tokenscope.ingestion.csv_reader import REQUIRED_COLUMNS, CsvBatchReader
from tokenscope.monitoring.service import MonitoringService


def request_json(**changes):
    value = {"messages": [{"role": "user", "content": "中文 request"}]}
    value.update(changes)
    return json.dumps(value, ensure_ascii=False, indent=2)


def csv_bytes(rows, header=REQUIRED_COLUMNS, bom=False):
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(header)
    writer.writerows(rows)
    return (("\ufeff" if bom else "") + output.getvalue()).encode("utf-8")


def valid_row(**changes):
    values = dict(
        zip(
            REQUIRED_COLUMNS,
            ("h1", "tenant", "2026-10-27T00:00:00.000000001Z", "12", request_json()),
            strict=True,
        )
    )
    values.update(changes)
    return [values[name] for name in REQUIRED_COLUMNS]


@pytest.fixture
def reader():
    return CsvBatchReader(DEFAULT_SETTINGS["GLM-5.2"])


@pytest.fixture
def service(tmp_path: Path):
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    return MonitoringService(inputs, tmp_path / "state")
