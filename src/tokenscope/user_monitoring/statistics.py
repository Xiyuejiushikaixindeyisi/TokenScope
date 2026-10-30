"""Exact, sparse user-only modal statistics; never changes V1/MA distributions."""

from collections.abc import Iterable
from fractions import Fraction
from typing import Any

WIDTHS = (1000, 2000, 5000)


def modal_bins(sorted_values: Iterable[int], count: int, width: int) -> dict[str, Any]:
    """Consume sorted C values with O(number of tied modal bins) memory."""
    if width not in WIDTHS or count < 0:
        raise ValueError("Invalid width or count")
    modes: list[dict[str, Any]] = []
    best = seen = total = 0
    previous = -1
    current_bin = -1
    bin_count = bin_sum = 0

    def finish() -> None:
        nonlocal modes, best
        if not bin_count:
            return
        row = dict(
            lower=str(current_bin * width),
            upper=str((current_bin + 1) * width),
            count=str(bin_count),
            sum_compute_tokens=str(bin_sum),
            share=bin_count / count if count else 0.0,
            mean={"numerator": str(bin_sum), "denominator": str(bin_count)},
        )
        if bin_count > best:
            best, modes = bin_count, [row]
        elif bin_count == best:
            modes.append(row)

    for value in sorted_values:
        if isinstance(value, bool) or not isinstance(value, int) or value < previous or value < 0:
            raise ValueError("Expected sorted nonnegative integer C values")
        key = value // width
        if key != current_bin:
            finish()
            current_bin, bin_count, bin_sum = key, 0, 0
        previous = value
        bin_count += 1
        bin_sum += value
        total += value
        seen += 1
    finish()
    if seen != count:
        raise ValueError("Count does not match facts")
    return {
        "count": str(seen),
        "total": str(total),
        "bin_width": width,
        "modes": modes,
        "representative": modes[0] if modes else None,
    }


def exact_mean(row: dict[str, Any]) -> Fraction:
    return Fraction(int(row["mean"]["numerator"]), int(row["mean"]["denominator"]))
