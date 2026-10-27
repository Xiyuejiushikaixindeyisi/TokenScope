"""Streaming exports of stored facts. The digest covers request lines including LF only."""

import csv
import hashlib
import io
import json
from collections.abc import Generator, Iterator
from typing import Any

from tokenscope.monitoring.view_models import canonical, sha
from tokenscope.monitoring.views import MonitoringViewService, RequestQuery

COLUMNS = (
    "service_instance_id",
    "view_schema_version",
    "run_id",
    "model_id",
    "appid",
    "settings_sha256",
    "source_record_index",
    "hash_id",
    "time_utc",
    "json_tokens",
    "prompt_tokens",
    "ideal_cached_input_tokens",
    "ideal_compute_input_tokens",
    "completion_tokens",
)


class ViewExport:
    def __init__(
        self, views: MonitoringViewService, run_id: str, appid: str, query: RequestQuery
    ) -> None:
        self.views, self.run_id, self.appid, self.query = views, run_id, appid, query
        snapshot = json.loads(views.snapshot(run_id, appid)[0])
        self.ident = views.context(snapshot["identity"])
        self.where, self.args = query.sql(appid)
        with views.projection(run_id) as db:
            self.count = db.execute(
                "SELECT count(*) FROM request_projection WHERE " + self.where, self.args
            ).fetchone()[0]
        provenance = snapshot["provenance"]
        self.settings_sha = sha(canonical(provenance["settings"]))
        self.metadata = dict(
            type="metadata",
            export_schema_version="1",
            **self.ident,
            input_sha256=provenance["input_sha256"],
            settings_sha256=self.settings_sha,
            data_range_utc=provenance["data_range_utc"],
            filter=query.filter(),
            sort=query.sort(),
            export_scope="filtered"
            if query.lower or query.upper is not None or query.hash_id is not None
            else "group",
            expected_rows=str(self.count),
        )

    def headers(self, format: str) -> dict[str, str]:
        result = {
            "Cache-Control": "no-store",
            "X-Export-Schema-Version": "1",
            "X-Export-Row-Count": str(self.count),
            "X-TokenScope-Instance-Id": self.ident["service_instance_id"],
            "X-Export-Run-Id": self.run_id,
            "Content-Disposition": f'attachment; filename="tokenscope-{self.run_id}.{format}"',
        }
        if format == "csv":
            result["X-CSV-Text-Escaping"] = "apostrophe"
        return result

    @staticmethod
    def csv_line(values: list[Any]) -> bytes:
        text = io.StringIO(newline="")
        csv.writer(text, lineterminator="\r\n").writerow(values)
        return text.getvalue().encode()

    def lines(self, format: str) -> Generator[bytes, None, None]:
        digest = hashlib.sha256()
        count = 0
        yield (
            canonical(self.metadata) + b"\n" if format == "ndjson" else self.csv_line(list(COLUMNS))
        )
        with self.views.projection(self.run_id) as db:
            cursor = db.execute(
                "SELECT * FROM request_projection WHERE " + self.where + self.query.order_sql(),
                self.args,
            )
            # Fetch one row, never buffer a batch of potentially huge hash IDs.
            for row in cursor:
                fact = self.views.fact(self.run_id, row)
                if format == "ndjson":
                    line = canonical(dict(type="request", **fact)) + b"\n"
                    digest.update(line)
                else:
                    values = {
                        **self.ident,
                        "settings_sha256": self.settings_sha,
                        "source_record_index": fact["request_ref"]["source_record_index"],
                        **fact,
                    }
                    cells = []
                    for key in COLUMNS:
                        value = values[key]
                        if key in ("model_id", "appid", "hash_id") and value[:1] in (
                            "=",
                            "+",
                            "-",
                            "@",
                            "\t",
                            "\r",
                            "\n",
                        ):
                            value = "'" + value
                        cells.append(value)
                    line = self.csv_line(cells)
                yield line
                count += 1
        if count != self.count:
            raise OSError("Export count changed")
        if format == "ndjson":
            yield (
                canonical(
                    dict(
                        type="summary",
                        actual_rows=str(count),
                        request_lines_sha256=digest.hexdigest(),
                    )
                )
                + b"\n"
            )

    def stream(self, format: str) -> Iterator[bytes]:
        # Network chunks <=64KiB; a single source row may exceed the 1MiB batch target.
        lines = self.lines(format)
        try:
            for line in lines:
                for start in range(0, len(line), 65536):
                    yield line[start : start + 65536]
        finally:
            lines.close()
