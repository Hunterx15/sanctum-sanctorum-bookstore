"""Member operations and tier helpers."""
from datetime import datetime
from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Loan, Member, MemberTier, Order, OrderStatus
from app.schemas import MemberCreate, MemberStats

# Tiers from lowest to highest; a member's rank is their index in this list.
TIER_ORDER: List[str] = [
    MemberTier.APPRENTICE.value,
    MemberTier.ADEPT.value,
    MemberTier.MASTER.value,
    MemberTier.SUPREME.value,
]

# Minimum tier allowed to buy or borrow restricted books.
RESTRICTED_MIN_TIER = MemberTier.MASTER.value


def tier_at_least(tier: str, minimum: str) -> bool:
    """True if ``tier`` ranks at or above ``minimum``."""
    return TIER_ORDER.index(tier) > TIER_ORDER.index(minimum)


def ensure_can_access_restricted(member: Member) -> None:
    """Raise 403 unless the member's tier may access restricted books."""
    if not tier_at_least(member.tier, RESTRICTED_MIN_TIER):
        raise HTTPException(
            status_code=403, detail=f"Restricted books require tier '{RESTRICTED_MIN_TIER}' or higher"
        )


def create_member(db: Session, data: MemberCreate, now: datetime) -> Member:
    """Register a member.

    Rules: email must be unique -> 409; created_at = now.
    """
    existing = db.scalar(
        select(Member).where(Member.email == data.email)
    )

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Email already exists",
        )

    member = Member(
        name=data.name,
        email=data.email,
        tier=data.tier.value,
        created_at=now,
    )

    db.add(member)
    db.commit()
    db.refresh(member)

    return member


def get_member(db: Session, member_id: int) -> Member:
    """Return a member by id, or raise 404."""
    member = db.get(Member, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


def list_member_orders(db: Session, member_id: int) -> List[Order]:
    """All orders of a member ordered by id ascending; 404 if the member is missing."""
    get_member(db, member_id)
    return list(db.scalars(select(Order).where(Order.member_id == member_id).order_by(Order.id)))


def get_member_stats(db: Session, member_id: int, now: datetime) -> MemberStats:
    """Summarize a member's activity."""

    # 404 if member does not exist
    get_member(db, member_id)

    # Only paid orders count
    paid_orders = db.scalars(
        select(Order).where(
            Order.member_id == member_id,
            Order.status == OrderStatus.PAID.value,
        )
    ).all()

    orders_paid = len(paid_orders)

    total_spent_cents = sum(
        order.total_cents
        for order in paid_orders
    )

    # All loans belonging to this member
    loans = db.scalars(
        select(Loan).where(Loan.member_id == member_id)
    ).all()

    # Every unreturned loan counts as active,
    # including overdue loans
    active_loans = sum(
        1
        for loan in loans
        if loan.returned_at is None
    )

    # Only unreturned loans past due date are overdue
    overdue_loans = sum(
        1
        for loan in loans
        if loan.returned_at is None and now > loan.due_at
    )

    # Late fees are summed from returned loans
    late_fees_cents = sum(
        loan.late_fee_cents
        for loan in loans
        if loan.returned_at is not None
    )

    return MemberStats(
        member_id=member_id,
        orders_paid=orders_paid,
        total_spent_cents=total_spent_cents,
        active_loans=active_loans,
        overdue_loans=overdue_loans,
        late_fees_cents=late_fees_cents,
    )
