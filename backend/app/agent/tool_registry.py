import json
import random
from pathlib import Path

from app.schemas import Tool

CATALOG_PATH = Path(__file__).resolve().parent.parent / "tools" / "catalog.json"


def load_catalog(path: Path = CATALOG_PATH) -> list[Tool]:
    with open(path, encoding="utf-8") as f:
        return [Tool(**t) for t in json.load(f)]


class ToolRegistry:
    """The set of tools offered to the agent for one request."""

    def __init__(self, tools: list[Tool]):
        names = [t.name for t in tools]
        if len(set(names)) != len(names):
            raise ValueError("duplicate tool names")
        self.tools = tools

    @classmethod
    def from_catalog(cls, n: int | None = None, order: str = "given", seed: int = 0,
                     path: Path = CATALOG_PATH) -> "ToolRegistry":
        """First n catalog tools, then ordered as given, reversed, or shuffled with a seed.

        The similarity factor for E5 (near-duplicate tools, up to 64 tools) is added in Phase 7;
        catalog entries already carry a `group` field for it.
        """
        tools = load_catalog(path)
        if n is not None:
            if n > len(tools):
                raise ValueError(f"n_tools={n} exceeds catalog size {len(tools)}")
            tools = tools[:n]
        if order == "reverse":
            tools = tools[::-1]
        elif order == "shuffle":
            tools = list(tools)
            random.Random(seed).shuffle(tools)
        elif order != "given":
            raise ValueError(f"unknown order: {order}")
        return cls(tools)

    def names(self) -> list[str]:
        return [t.name for t in self.tools]

    def has(self, name: str) -> bool:
        return name in self.names()

    def get(self, name: str) -> Tool:
        for t in self.tools:
            if t.name == name:
                return t
        raise KeyError(name)
