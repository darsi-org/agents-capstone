"""Milestone 1: tests for your MCP tools. One example is here; add at least two more (check.py counts them in this file),
including free_rooms, draft_message and a day that does not exist."""
from tools.server import find_lessons


def test_find_lessons_in_period_order():
    periods = [int(r["period"]) for r in find_lessons("2B", "Tue")]
    assert periods == sorted(periods) and periods
