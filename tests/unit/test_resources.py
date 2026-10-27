import os

import pytest

from tokenscope.errors import TokenScopeError
from tokenscope.resources import configure_process


def test_process_budget_limits_native_pools_and_affinity(monkeypatch):
    chosen = []
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: {2, 3, 4, 5})
    monkeypatch.setattr(os, "sched_setaffinity", lambda pid, cpus: chosen.extend(cpus))
    for key in [
        "OPENBLAS_NUM_THREADS",
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "RAYON_NUM_THREADS",
    ]:
        monkeypatch.setenv(key, "99")
    configure_process(2)
    assert chosen == [2, 3]
    assert os.environ["RAYON_NUM_THREADS"] == "2"
    assert os.environ["OPENBLAS_NUM_THREADS"] == "1"
    with pytest.raises(TokenScopeError):
        configure_process(0)
