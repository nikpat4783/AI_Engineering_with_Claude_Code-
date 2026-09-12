import logging
from datetime import datetime, UTC
from typing import Optional

logger = logging.getLogger(__name__)

_idempotency_cache = {}

APPROVAL_THRESHOLD = 100000.00  # Rs 1,00,000 requires approval


def interchange_fee(
    amount: float, idempotency_key: Optional[str] = None, approved: bool = False
) -> float:
    """UniPay spec: 1.10% of amount + Rs 2.50 flat, rounded to 2 decimals.

    Args:
        amount: Transaction amount in rupees
        idempotency_key: Optional key to prevent duplicate fee calculations
        approved: Whether transaction has been approved (required for large amounts)

    Returns:
        Calculated fee amount

    Raises:
        ValueError: If idempotency_key indicates duplicate payment or approval required
    """
    if amount < 0:
        raise ValueError(f"Amount must be non-negative, got {amount}")

    if amount > APPROVAL_THRESHOLD and not approved:
        logger.warning(
            f"Large transaction requires approval",
            extra={"amount": amount, "threshold": APPROVAL_THRESHOLD},
        )
        raise ValueError(
            f"Amount {amount} exceeds approval threshold {APPROVAL_THRESHOLD}"
        )

    if idempotency_key:
        if idempotency_key in _idempotency_cache:
            cached_result = _idempotency_cache[idempotency_key]
            logger.warning(
                f"Duplicate fee calculation attempt",
                extra={
                    "idempotency_key": idempotency_key,
                    "previous_amount": cached_result["amount"],
                    "previous_fee": cached_result["fee"],
                }
            )
            raise ValueError(
                f"Duplicate payment detected for idempotency_key={idempotency_key}"
            )

    fee = round(amount * 0.011 + 2.50, 2)

    if idempotency_key:
        _idempotency_cache[idempotency_key] = {
            "amount": amount,
            "fee": fee,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    logger.info(
        "Interchange fee calculated",
        extra={
            "amount": amount,
            "fee": fee,
            "idempotency_key": idempotency_key,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )

    return fee