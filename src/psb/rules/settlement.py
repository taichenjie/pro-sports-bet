"""Asian Handicap settlement, including quarter lines.

A quarter line (e.g. -0.75) is two half-stakes on the neighbouring lines
(-0.5 and -1.0). Each half settles on its own; the results are averaged.
"""

from __future__ import annotations

# Return per 1 unit staked, excluding the stake: win = odds - 1, push = 0, loss = -1.


def _settle_simple(line: float, margin: int, odds: float) -> float:
    """Settle a whole or half line. margin = backed team's goals minus opponent's."""
    adjusted = margin + line
    if adjusted > 0:
        return odds - 1.0
    if adjusted == 0:
        return 0.0
    return -1.0


def split_line(line: float) -> tuple[float, float]:
    """Split a handicap into its two half-stake lines (identical for whole/half lines)."""
    quarters = round(line * 4)
    if quarters % 2 == 0:  # whole or half line
        return (line, line)
    return ((quarters - 1) / 4, (quarters + 1) / 4)


def settle_ah(line: float, backed_goals: int, opponent_goals: int, odds: float) -> float:
    """Profit per 1 unit staked on the backed side at the given handicap line."""
    margin = backed_goals - opponent_goals
    low, high = split_line(line)
    return 0.5 * _settle_simple(low, margin, odds) + 0.5 * _settle_simple(high, margin, odds)


def expected_value_ah(line: float, odds: float, margin_probs: dict[int, float]) -> float:
    """Expected profit per unit, given P(backed margin = m) for each goal margin m."""
    return sum(
        p * 0.5 * (_settle_simple(a, m, odds) + _settle_simple(b, m, odds))
        for m, p in margin_probs.items()
        for a, b in [split_line(line)]
    )
