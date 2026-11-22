import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import run_superstar_holdings as sh  # noqa: E402

Q = ["2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31"]


def series(*pcts):
    return list(zip(Q[-len(pcts):], pcts))


def test_never_held():
    assert sh.classify(series(None, None)) is None


def test_single_quarter_is_holding():
    row = sh.classify(series(2.5))
    assert row["status"] == sh.HOLDING
    assert row["latest_pct"] == 2.5


def test_new_buy():
    row = sh.classify(series(None, None, 1.4))
    assert row["status"] == sh.NEW
    assert row["change_pct"] == 1.4
    assert row["first_seen_quarter"] == Q[-1]


def test_increase_streak():
    row = sh.classify(series(1.0, 1.5, 2.0, 2.6))
    assert row["status"] == sh.INCREASED
    assert row["consecutive_increases"] == 3
    assert row["below_max"] is False


def test_decrease_and_below_max():
    row = sh.classify(series(3.0, 2.0, 2.0, 1.5))
    assert row["status"] == sh.DECREASED
    assert row["max_pct"] == 3.0
    assert row["drop_from_max_pct"] == 1.5
    assert row["below_max"] is True


def test_unchanged_but_below_peak():
    row = sh.classify(series(4.0, 2.0, 2.0))
    assert row["status"] == sh.UNCHANGED
    assert row["below_max"] is True


def test_exit():
    row = sh.classify(series(1.2, 1.1, None))
    assert row["status"] == sh.EXITED
    assert row["latest_pct"] == 0.0
    assert row["last_held_pct"] == 1.1


def test_reentry_is_new():
    row = sh.classify(series(2.0, None, 1.3))
    assert row["status"] == sh.NEW


def test_score_high_for_raise_with_company():
    row = sh.classify(series(1.0, 1.5, 2.0))
    out = sh.score_conviction(
        row, "Vijay Kedia", 3, {"conviction": "High", "sentiment": "Bullish", "probability_score": 70},
        {"news_sentiment": "Bullish", "news_headline": "Order win"}, None, ["Strong ROE"],
    )
    assert out["conviction"] == "High"
    assert out["why"].startswith("Vijay Kedia raised")


def test_score_low_for_exit():
    row = sh.classify(series(1.2, None))
    out = sh.score_conviction(row, "Dolly Khanna", 1, None, None, None, None)
    assert out["conviction"] == "Low"
    assert out["sentiment"] == "Bearish"


def test_needs_check():
    today = date(2026, 11, 22)
    assert sh.last_quarter_end(today) == date(2026, 9, 30)
    assert sh.needs_check(None, today, 3, False)
    assert not sh.needs_check({"last_quarter": "2026-09-30"}, today, 3, False)
    recent = {"last_quarter": "2026-06-30", "checked_at": datetime.now() - timedelta(days=1)}
    assert not sh.needs_check(recent, today, 3, False)
    assert sh.needs_check(recent, today, 3, True)


def test_match_investor_sums_rows():
    rows = [
        {"COL_I": "VIJAY KISHANLAL KEDIA", "COL_VIII": "1.20"},
        {"COL_I": "Kedia Securities Private Limited", "COL_VIII": "0.9"},
        {"COL_I": "Someone Else", "COL_VIII": "5"},
    ]
    pct, names = sh.match_investor(rows, ["Vijay Kedia", "Vijay Kishanlal Kedia", "Kedia Securities"])
    assert round(pct, 2) == 2.1
    assert len(names) == 2
