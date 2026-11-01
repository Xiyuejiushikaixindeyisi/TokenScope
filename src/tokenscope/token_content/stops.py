"""Local stop position added without modifying the public cooperative control."""

from tokenscope.analysis_common.plugins import ExecutionStopped, RunControl


class LocatedStop(ExecutionStopped):
    def __init__(self, code: str, location: str) -> None:
        super().__init__(code)
        self.stop_location = location


def consume(control: RunControl, resource: str, amount: int, location: str) -> None:
    try:
        control.consume(resource, amount)
    except ExecutionStopped as exc:
        raise LocatedStop(exc.code, location) from exc
