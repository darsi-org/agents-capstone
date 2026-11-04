"""School-helper tools as an MCP server. Made-up data only; draft_message saves a draft and never sends."""
import csv
import pathlib

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("school-helper")
ROOT = pathlib.Path(__file__).resolve().parents[1]
DAYS = {"Sun", "Mon", "Tue", "Wed", "Thu"}


def rows():
    with open(ROOT / "data/timetable.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@mcp.tool()
def find_lessons(cls: str, day: str) -> list[dict]:
    """Lessons for one class on one day (Sun to Thu), in period order."""
    if day not in DAYS:
        raise ValueError(f"unknown day {day!r}")
    return sorted((r for r in rows() if r["class"] == cls and r["day"] == day), key=lambda r: int(r["period"]))


# TODO milestone 1: free_rooms(day, period) and draft_message(to, text), which writes only inside drafts/.

if __name__ == "__main__":
    mcp.run()
