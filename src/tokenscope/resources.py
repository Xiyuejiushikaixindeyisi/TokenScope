"""Resource limits for the dedicated CLI/service process, before native pools initialize."""

import os

from tokenscope.errors import TokenScopeError


def configure_process(cpu_budget: int) -> None:
    if cpu_budget <= 0:
        raise TokenScopeError("INVALID_CPU_BUDGET", "CPU budget must be positive", 422)
    for name in (
        "OPENBLAS_NUM_THREADS",
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    ):
        os.environ[name] = "1"
    os.environ["RAYON_NUM_THREADS"] = str(cpu_budget)
    if hasattr(os, "sched_getaffinity"):
        available = sorted(os.sched_getaffinity(0))
        os.sched_setaffinity(0, available[:cpu_budget])
