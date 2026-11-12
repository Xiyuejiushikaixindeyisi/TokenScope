import json

from conftest import csv_bytes, valid_row

from tokenscope.analysis_common.contracts import SourceSelection
from tokenscope.analysis_common.contracts_v3 import PreparationRequest3
from tokenscope.analysis_common.service_v3 import PreparationService
from tokenscope.domain import RunSubmission
from tokenscope.user_monitoring.service import UserRunService


def test_more_than_32_real_recipes_finish_with_one_baseline(service):
    rows = []
    for template in range(34):
        for day in (10, 11):
            body = {
                "messages": [
                    {
                        "role": "system",
                        "content": f"template-{template:02d} stable " * 8
                        + f"<session_clock>2026/11/{day}</session_clock>",
                    },
                    {"role": "user", "content": "hello"},
                ]
            }
            rows.append(
                valid_row(appid="many", hash_id=f"h{len(rows)}", request_input=json.dumps(body))
            )
    (service.inputs.root / "many.csv").write_bytes(csv_bytes(rows))
    run = service.submit(RunSubmission(file_ref="many.csv", model_id="GLM-5.2"))
    assert service.processor.process_next().status == "completed"
    prep = PreparationService(service, UserRunService(service))
    receipt = prep.store.submit(
        PreparationRequest3(
            submission_key="many",
            source=SourceSelection(source_kind="base", base_run_id=run.run_id, appid="many"),
        )
    )
    assert prep.process_next().state == "completed"
    task = prep.diagnoses.submit(receipt.preparation_id, "many")
    execution = prep.process_next()
    report = prep.diagnoses.report(task.task_id)
    assert len(report["recommendations"]) >= 34
    assert all(r["windows"][0]["complete"] for r in report["recommendations"]), report
    assert len(execution.checkpoints) > 128
    assert not execution.forced_termination
    assert not any(
        "BUDGET_EXHAUSTED" in w.get("reason_code", "")
        for r in report["recommendations"]
        for w in r["windows"]
        if w.get("reason_code")
    )
