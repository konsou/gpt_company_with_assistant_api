import dataclasses
from abc import ABC, abstractmethod


class Tool(ABC):
    @property
    def name(self) -> str:
        return self.__class__.__name__.lower()

    @abstractmethod
    def function(self, *args, **kwargs):
        pass


@dataclasses.dataclass
class ToolCall:
    tool: Tool
    caller: str
    args: tuple | None
    kwargs: dict | None

    def call(self) -> str:
        # Got args and kwargs
        if self.args is not None and self.kwargs is not None:
            return self.tool.function(*self.args, **self.kwargs, caller=self.caller)

        # Got only args
        if self.args is not None:
            return self.tool.function(*self.args, caller=self.caller)

        # Got only kwargs
        if self.kwargs is not None:
            return self.tool.function(**self.kwargs, caller=self.caller)

        # Got neither
        return self.tool.function(caller=self.caller)
