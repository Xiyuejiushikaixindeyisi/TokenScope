import json
import sqlite3

import pytest

from tokenscope.user_monitoring.projection import populate


def project(values):
    source, target = sqlite3.connect(":memory:"), sqlite3.connect(":memory:")
    source.execute(
        "CREATE TABLE facts(appid,prompt_tokens,ideal_cached_input_tokens,"
        "ideal_compute_input_tokens)"
    )
    source.executemany("INSERT INTO facts VALUES('a',?,0,?)", [(v, v) for v in values])
    populate(source, target)
    source.close()
    return target


@pytest.mark.parametrize(
    "values,lower,count,total,ties",
    [
        ([100, 200, 6100], 0, 2, 300, 1),
        ([100, 6100], 0, 1, 100, 2),
        ([0, 4999, 5000, 199999, 200000], 0, 2, 4999, 1),
        ([2**62] * 5, (2**62 // 5000) * 5000, 5, 5 * 2**62, 1),
    ],
)
def test_exact_sparse_modes(values, lower, count, total, ties):
    db = project(values)
    row = json.loads(db.execute("SELECT payload FROM groups WHERE width=5000").fetchone()[0])
    assert row["representative_bin"]["lower"] == str(lower)
    assert row["representative_bin"]["count"] == str(count)
    assert row["representative_bin"]["sum_compute_tokens"] == str(total)
    assert row["tie_count"] == str(ties)
    for width in (1000, 2000, 5000):
        bins = [
            json.loads(r[0]) for r in db.execute("SELECT payload FROM bins WHERE width=?", (width,))
        ]
        assert sum(int(b["count"]) for b in bins) == len(values)
        assert sum(int(b["sum_compute_tokens"]) for b in bins) == sum(values)
    db.close()


def test_empty_and_missing_facts():
    db = project([])
    assert db.execute("SELECT count(*) FROM groups").fetchone()[0] == 0
    db.close()
    from tokenscope.errors import TokenScopeError

    with pytest.raises(TokenScopeError, match="facts"):
        populate(sqlite3.connect(":memory:"), sqlite3.connect(":memory:"))
