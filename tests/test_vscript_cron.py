"""Issue #1 D: the cron implementation had no tests."""
from __future__ import annotations

from datetime import datetime

import pytest

from pyvdisk.vscript.cron import CronError, CronExpression, cron, parse_cron


def test_every_minute_matches_and_advances_one_minute():
    expr = cron("* * * * *")
    assert expr.matches(datetime(2026, 9, 24, 8, 30))
    assert expr.next_after(datetime(2026, 9, 24, 8, 30)) == datetime(2026, 9, 24, 8, 31)


def test_fields_are_combined_with_and():
    expr = cron("30 8 * * *")
    assert expr.matches(datetime(2026, 9, 24, 8, 30))          # Thursday 08:30
    assert expr.matches(datetime(2026, 9, 23, 8, 30))          # day field is '*'
    assert not expr.matches(datetime(2026, 9, 24, 8, 31))
    assert not expr.matches(datetime(2026, 9, 24, 9, 30))


def test_lists_ranges_and_steps():
    assert cron("0,30 * * * *").matches(datetime(2026, 9, 24, 10, 30))
    assert not cron("0,30 * * * *").matches(datetime(2026, 9, 24, 10, 15))
    assert cron("*/15 * * * *").matches(datetime(2026, 9, 24, 10, 45))
    assert not cron("*/15 * * * *").matches(datetime(2026, 9, 24, 10, 46))
    assert cron("0 9-17 * * *").matches(datetime(2026, 9, 24, 17, 0))
    assert not cron("0 9-17 * * *").matches(datetime(2026, 9, 24, 18, 0))


def test_weekday_seven_is_sunday():
    sunday = datetime(2026, 9, 27)
    assert sunday.weekday() == 6
    assert cron("0 0 * * 7").matches(sunday)
    assert cron("0 0 * * 0").matches(sunday)          # both spellings of Sunday
    assert not cron("0 0 * * 1-5").matches(sunday)
    assert cron("0 0 * * 1-5").matches(datetime(2026, 9, 24))  # Thursday


def test_day_of_month_and_month_together():
    expr = cron("0 0 1 3 *")                           # midnight, 1 March
    assert expr.matches(datetime(2026, 3, 1))
    assert not expr.matches(datetime(2026, 4, 1))
    assert expr.next_after(datetime(2026, 1, 5)) == datetime(2026, 3, 1)


def test_next_after_skips_ahead_and_normalises_seconds():
    assert cron("0 12 * * *").next_after(datetime(2026, 9, 24, 13, 0)) == datetime(2026, 9, 25, 12, 0)
    assert cron("0 0 * * *").next_after(datetime(2026, 1, 5, 23, 59, 59, 500)) == datetime(2026, 1, 6, 0, 0)


def test_an_impossible_date_never_matches():
    expr = cron("0 0 30 2 *")                          # 30 February
    assert not any(expr.matches(datetime(2026, 2, day)) for day in range(1, 29))


@pytest.mark.parametrize("bad", [
    "",                       # no fields
    "* * * *",                # four fields
    "* * * * * *",            # six fields
    "60 * * * *",             # minute out of range
    "* 24 * * *",             # hour out of range
    "* * 0 * *",              # day 0 is not a day
    "* * 32 * *",
    "* * * 0 *",
    "* * * 13 *",
    "* * * * 8",              # weekday out of range
    "*/0 * * * *",            # zero step
    "-1 * * * *",
    "5/2 * * * *",            # step without a range
    "1-2-3 * * * *",
    "1,,2 * * * *",
    "a * * * *",
    "*/x * * * *",
    "1-5/ * * * *",
])
def test_invalid_expressions_are_rejected(bad):
    with pytest.raises(CronError):
        cron(bad)


def test_non_string_expressions_are_rejected():
    for bad in (5, None, ["* * * * *"]):
        with pytest.raises(CronError):
            cron(bad)


def test_matching_requires_a_datetime():
    expr = cron("* * * * *")
    with pytest.raises(TypeError):
        expr.matches("2026-09-24")
    with pytest.raises(TypeError):
        expr.next_after(5)


def test_expression_is_normalised_and_repr_is_stable():
    expr = parse_cron("  0   0  *  *  * ")
    assert isinstance(expr, CronExpression)
    assert expr.expression == "0 0 * * *"
    assert repr(expr) == "CronExpression('0 0 * * *')"


def test_match_is_an_alias_for_matches():
    expr = cron("0 0 * * *")
    value = datetime(2026, 9, 24)
    assert expr.match(value) == expr.matches(value)
