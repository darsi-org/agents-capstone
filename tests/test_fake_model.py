"""The fake model gives scripted replies (a tool call, then an answer) in order, as your agent tests need."""
from fake_model import scripted, tool_call


def test_scripted_replies_come_in_order():
    model = scripted(tool_call("find_lessons", cls="2B", day="Tue"), "Class 2B has Science first.").bind_tools([])
    first = model.invoke("What does 2B have on Tuesday?")
    assert first.tool_calls[0]["name"] == "find_lessons"
    assert first.tool_calls[0]["args"] == {"cls": "2B", "day": "Tue"}
    assert model.invoke("Thanks").content == "Class 2B has Science first."
