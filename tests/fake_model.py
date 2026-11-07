"""A scripted stand-in for the model, so tests and GitHub Actions run without Ollama or a GPU.

    from fake_model import scripted, tool_call

    model = scripted(tool_call("find_lessons", cls="2B", day="Tue"), "Class 2B has Science first.")
    graph = make_graph(model)  # build agent.py's graph from a model you pass in

Each call to the model returns the next scripted reply, in order: a tool call or a plain answer.
"""
from itertools import count

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

_ids = count(1)


class FakeToolModel(GenericFakeChatModel):
    """GenericFakeChatModel that also accepts bind_tools(), like a real chat model."""

    def bind_tools(self, tools, **kwargs):
        return self


def tool_call(name, **args):
    """A reply that asks for one tool call."""
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": f"call_{next(_ids)}", "type": "tool_call"}])


def scripted(*replies):
    """A fake model that gives these replies in order (strings become plain answers)."""
    return FakeToolModel(messages=iter([r if isinstance(r, AIMessage) else AIMessage(content=str(r)) for r in replies]))
