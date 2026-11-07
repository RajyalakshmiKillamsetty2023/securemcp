"""Offline keyword picker for laptop development and tests.

Not a language model. It must never be used for experiments: results from it say nothing
about real agents. It reads the prompt built by app.agent.prompts and picks the tool whose
description shares the most words with the query.
"""
import json
import re

from app.llm.client import LLMClient

_STOP = {"the", "and", "for", "what", "with", "from", "that", "this", "are", "you", "can",
         "how", "your", "please", "give", "tell"}
_TOOL_RE = re.compile(r"^- (\w+): (.*)$", re.MULTILINE)
_PARAMS_RE = re.compile(r"^  parameters: (\{.*\})$", re.MULTILINE)
_QUERY_RE = re.compile(r"^Query: (.*?)\nAnswer:", re.MULTILINE | re.DOTALL)
_EXPR_RE = re.compile(r"\d[\d\s+\-*/().%^]*[+\-*/%^][\d\s+\-*/().%^]*\d")


def _tokens(text: str) -> set[str]:
    out = set()
    for t in re.findall(r"[a-z0-9]+", text.lower().replace("_", " ")):
        t = t[:-1] if t.endswith("s") and len(t) > 3 else t
        if len(t) > 2 and t not in _STOP:
            out.add(t)
    return out


class MockLLMClient(LLMClient):
    model = "mock-keyword-v1"

    def complete(self, prompt: str, temperature: float = 0.0) -> str:
        qm = _QUERY_RE.search(prompt)
        query = qm.group(1).strip() if qm else ""
        names = _TOOL_RE.findall(prompt)
        param_lines = _PARAMS_RE.findall(prompt)
        expr = _EXPR_RE.search(query)
        q_tokens = _tokens(query)

        best, best_score, best_params = None, 0, {}
        for (name, desc), plines in zip(names, param_lines, strict=False):
            params = json.loads(plines)
            score = len(q_tokens & _tokens(name + " " + desc))
            if expr and "expression" in params:
                score += 1
            if score > best_score:
                best, best_score, best_params = name, score, params
        if best is None:
            return json.dumps({"tool": None, "arguments": {}})
        return json.dumps({"tool": best, "arguments": self._fill(best_params, query, expr)})

    @staticmethod
    def _fill(params: dict, query: str, expr) -> dict:
        numbers = re.findall(r"-?\d+(?:\.\d+)?", query)
        words = re.findall(r"\b[A-Z][A-Za-z]+\b", query)
        if words and query.startswith(words[0]):
            words = words[1:]
        date = re.search(r"\d{4}-\d{2}-\d{2}", query)
        args = {}
        for name, ptype in params.items():
            if "expression" in name and expr:
                args[name] = expr.group(0).strip()
            elif ptype in ("number", "integer") and numbers:
                args[name] = float(numbers.pop(0)) if ptype == "number" else int(float(numbers.pop(0)))
            elif "date" in name and date:
                args[name] = date.group(0)
            elif ptype == "string" and words:
                args[name] = words.pop(0)
            else:
                args[name] = "unknown"
        return args
