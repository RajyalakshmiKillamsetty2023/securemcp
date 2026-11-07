from abc import ABC, abstractmethod


class LLMClient(ABC):
    model: str

    @abstractmethod
    def complete(self, prompt: str, temperature: float = 0.0) -> str:
        """Return the model's text reply to a single prompt."""
