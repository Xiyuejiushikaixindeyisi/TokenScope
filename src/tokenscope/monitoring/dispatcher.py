"""Round-robin dispatch. Each processor owns the shared worker.lock itself."""

import threading
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel


class Processor(Protocol):
    def process_next(self) -> BaseModel | None: ...


class Dispatcher:
    def __init__(self, *processors: Processor, state_root: Path | None = None) -> None:
        self.processors = list(processors)
        self.position = 0
        self.lock = threading.Lock()
        self.state_root = state_root

    def register(self, processor: Processor) -> None:
        with self.lock:
            if processor not in self.processors:
                self.processors.append(processor)

    def process_next(self) -> BaseModel | None:
        # Persist rotation across short CLI processes. This lock protects only dispatch;
        # every processor still owns the original worker.lock across execution/recovery.
        with self.lock:
            if self.state_root is None:
                return self._next()
            import fcntl

            with (self.state_root / "dispatcher.cursor").open("a+") as stream:
                try:
                    fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    return None
                stream.seek(0)
                value = stream.read(32).strip()
                self.position = int(value) % max(1, len(self.processors)) if value.isdigit() else 0
                try:
                    return self._next()
                finally:
                    stream.seek(0)
                    stream.truncate()
                    stream.write(str(self.position))
                    stream.flush()

    def _next(self) -> BaseModel | None:
        for _ in range(len(self.processors)):
            processor = self.processors[self.position]
            self.position = (self.position + 1) % len(self.processors)
            result = processor.process_next()
            if result is not None:
                return result
        return None
