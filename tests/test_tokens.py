"""Token 估算单测。"""

from src.utils.tokens import check_document_fits_context, estimate_request_tokens


def test_estimate_positive():
    n = estimate_request_tokens("hello", "system", "extra")
    assert n >= 1


def test_check_fits():
    assert check_document_fits_context(100, 1000) is None


def test_check_exceeds():
    err = check_document_fits_context(2000, 1000)
    assert err is not None
    assert err.code == "token_limit"
