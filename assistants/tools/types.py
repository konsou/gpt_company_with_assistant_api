import dataclasses
from abc import ABC, abstractmethod
from typing import Callable


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
    args: tuple
    kwargs: dict

    def call(self) -> str:
        return self.tool.function(*self.args, **self.kwargs, caller=self.caller)


if __name__ == "__main__":
    t = Tool(print)
    print(t.name)
    print(type(t.name))
