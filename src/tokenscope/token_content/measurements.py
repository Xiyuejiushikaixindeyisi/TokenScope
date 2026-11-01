"""Source content measures, never estimated Token attribution."""

from tokenscope.token_content.json_values import Value, dumps

MEASUREMENT_VERSION = "content-measures-1"


def measure(value: Value) -> dict[str, int]:
    if isinstance(value, str):
        return {
            "utf8_bytes": len(value.encode("utf-8")),
            "unicode_codepoints": len(value),
            "lines": len(value.splitlines()),
        }
    result = {"display_json_utf8_bytes": len(dumps(value, sort_keys=True).encode("utf-8"))}
    if isinstance(value, list):
        result["items"] = len(value)
    if isinstance(value, dict):
        result["fields"] = len(value)
    return result
