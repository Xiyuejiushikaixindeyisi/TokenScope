"""Complete original request pairs, constrained to a previously resolved scope."""

from tokenscope.analysis_common.contracts import RequestComparison
from tokenscope.analysis_common.source import ResolvedSource
from tokenscope.errors import TokenScopeError


def read_comparison(source: ResolvedSource, comparison: RequestComparison) -> tuple[str, str]:
    source.verify()
    left = source.read_request(comparison.left)
    right = source.read_request(comparison.right)
    if (
        left.raw_sha256 != comparison.left_raw_sha256
        or right.raw_sha256 != comparison.right_raw_sha256
    ):
        raise TokenScopeError("EVIDENCE_CHANGED", "Original comparison identity changed", 409)
    return left.raw_body, right.raw_body
