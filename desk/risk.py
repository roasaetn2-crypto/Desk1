"""Seat 4: the risk engine. Plain Python. No model touches this file. Ever.

It decides whether a trade happens and how big it is. It cannot be argued with,
which is the entire point.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from config import EXITS, MIN_SCORE, RISK


@dataclass
class Account:
    equity: float
    day_pnl: float
    open_positions: int


def in_quiet_hours(now: datetime | None = None) -> bool:
    """True when new entries are blocked.

    `quiet_hours` is a (start, end) pair of local hours. A wrapping window such
    as (22, 6) means 22:00 -> 06:00. An empty/equal pair means the window is
    disabled: the desk trades around the clock.

    This used to fall through to the wrap-around branch for (0, 0), which
    evaluated `h >= 0 or h < 0` -- always true -- so setting quiet hours to
    (0, 0) to turn them off actually blocked every entry, all day. That is why
    the desk looked alive and never traded.
    """
    window = RISK.get("quiet_hours")
    if not window:
        return False
    start, end = window
    if start == end:
        return False
    h = (now or datetime.now()).hour
    return start <= h < end if start < end else (h >= start or h < end)


def check_token_trade(thesis, account: Account, liquidity_usd: float,
                      now: datetime | None = None) -> tuple[bool, float, str]:
    """Return (approved, ticket_usd, reason)."""
    if account.day_pnl <= -RISK["max_daily_loss_pct"] * account.equity:
        return False, 0.0, "daily loss limit hit, desk halted until tomorrow"
    if in_quiet_hours(now):
        return False, 0.0, "quiet hours, no new entries"
    if thesis.verdict != "valid_setup":
        return False, 0.0, f"analyst verdict: {thesis.verdict}"
    if thesis.score < MIN_SCORE:
        return False, 0.0, f"score {thesis.score} < {MIN_SCORE}"
    if account.open_positions >= RISK["max_open_positions"]:
        return False, 0.0, "max open positions"

    by_risk = RISK["max_risk_per_trade"] * account.equity / EXITS["stop_pct"]
    by_size = RISK["max_position_pct"] * account.equity
    by_pool = RISK["max_pool_share"] * liquidity_usd
    ticket = round(min(by_risk, by_size, by_pool), 2)
    if ticket < RISK["min_ticket_usd"]:
        return False, 0.0, f"ticket ${ticket} below fee floor ${RISK['min_ticket_usd']}"
    return True, ticket, "approved"


def sizing_breakdown(account: Account, liquidity_usd: float) -> dict:
    """The three caps, for the dashboard. The smallest one wins."""
    by_risk = RISK["max_risk_per_trade"] * account.equity / EXITS["stop_pct"]
    by_size = RISK["max_position_pct"] * account.equity
    by_pool = RISK["max_pool_share"] * liquidity_usd
    return {
        "by_risk": round(by_risk, 2),
        "by_size": round(by_size, 2),
        "by_pool": round(by_pool, 2),
        "ticket": round(min(by_risk, by_size, by_pool), 2),
    }


def check_live_trade(thesis, day_pnl: float, open_positions: int, liquidity_usd: float,
                     caps: dict, now: datetime | None = None) -> tuple[bool, float, str]:
    """The live version of seat 4. Same gates, but sized from the live caps.

    Paper sizes off a $1,000 book with 2% positions. That is right for a
    simulator and wrong for real money, where the cap IS the bankroll. Here the
    ticket is the smallest of: the per-trade cap, what is left of the total
    notional cap, and 2% of the pool. The broker re-checks all of it before it
    builds a transaction, so this is the first of two locks, not the only one.
    """
    if day_pnl <= -caps["daily_loss_usd"]:
        return False, 0.0, (f"live daily loss limit hit (${day_pnl:.2f} of "
                            f"-${caps['daily_loss_usd']:.2f})")
    if in_quiet_hours(now):
        return False, 0.0, "quiet hours, no new entries"
    if thesis.verdict != "valid_setup":
        return False, 0.0, f"analyst verdict: {thesis.verdict}"
    if thesis.score < MIN_SCORE:
        return False, 0.0, f"score {thesis.score} < {MIN_SCORE}"
    if open_positions >= RISK["max_open_positions"]:
        return False, 0.0, "max open positions"

    remaining = max(0.0, caps["max_notional"] - caps.get("deployed", 0.0))
    by_pool = RISK["max_pool_share"] * liquidity_usd
    ticket = round(min(caps["max_trade"], remaining, by_pool), 2)
    if ticket < RISK["min_ticket_usd"]:
        return False, 0.0, f"ticket ${ticket} below fee floor ${RISK['min_ticket_usd']}"
    return True, ticket, "approved"


def live_sizing_breakdown(liquidity_usd: float, caps: dict) -> dict:
    remaining = max(0.0, caps["max_notional"] - caps.get("deployed", 0.0))
    by_pool = RISK["max_pool_share"] * liquidity_usd
    return {
        "by_risk": caps["max_trade"],
        "by_size": remaining,
        "by_pool": round(by_pool, 2),
        "ticket": round(min(caps["max_trade"], remaining, by_pool), 2),
    }
