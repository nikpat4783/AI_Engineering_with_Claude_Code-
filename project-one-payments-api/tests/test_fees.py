import pytest
from src.fees import interchange_fee

def test_fee_on_1000():
    assert interchange_fee(1000) == 13.50

def test_fee_on_250():
    assert interchange_fee(250) == 5.25


def test_idempotency_prevents_duplicate():
    """Verify that duplicate idempotency keys raise an error"""
    idempotency_key = "txn-12345"
    fee1 = interchange_fee(1000, idempotency_key=idempotency_key)
    assert fee1 == 13.50

    with pytest.raises(ValueError, match="Duplicate payment detected"):
        interchange_fee(1000, idempotency_key=idempotency_key)


def test_different_idempotency_keys_allowed():
    """Verify that different idempotency keys can be processed"""
    fee1 = interchange_fee(1000, idempotency_key="txn-001")
    fee2 = interchange_fee(1000, idempotency_key="txn-002")
    assert fee1 == fee2 == 13.50


def test_boundary_zero_amount():
    """Verify fee calculation for zero amount"""
    assert interchange_fee(0) == 2.50


def test_boundary_small_amount():
    """Verify fee calculation for small amounts"""
    assert interchange_fee(1) == round(1 * 0.011 + 2.50, 2)
    assert interchange_fee(10) == round(10 * 0.011 + 2.50, 2)


def test_boundary_large_amount_without_approval():
    """Verify that large amounts require approval"""
    with pytest.raises(ValueError, match="exceeds approval threshold"):
        interchange_fee(200000)


def test_boundary_large_amount_with_approval():
    """Verify that approved large amounts are accepted"""
    fee = interchange_fee(200000, approved=True)
    assert fee == round(200000 * 0.011 + 2.50, 2)


def test_negative_amount_rejected():
    """Verify that negative amounts are rejected"""
    with pytest.raises(ValueError, match="must be non-negative"):
        interchange_fee(-1000)