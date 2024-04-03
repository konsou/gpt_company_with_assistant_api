from typing import Collection

from assistants.tools.shell import Shell
from assistants.tools.tag_parser import ToolTagParser, ParseResult
from assistants.tools.abc import Tool, ToolCall
import message_bus
from workspace import Workspace, DummyWorkspace
from .message import Message
from .save import Save


class ToolParser:
    def __init__(self, workspace: Workspace, message_bus: message_bus.MessageBus):
        self.workspace = workspace
        self.message_bus = message_bus
        # ADD NEW TOOLS HERE
        self.all_tools = (
            Shell(workspace=workspace),
            Message(message_bus=message_bus),
            Save(workspace=workspace),
        )
        self.tags_to_split_per_line = ("shell",)
        self.tools_by_name: dict[str, Tool] = {t.name: t for t in self.all_tools}
        self._parser = ToolTagParser(tags=self.tools_by_name.keys())

    def parse(self, text: str, caller: str) -> tuple[ToolCall, ...]:
        self._parser.reset()
        self._parser.feed(text)
        self._parser.close()
        parsed_tags: list[ParseResult] = self._parser.parsed_tags
        tool_calls = []
        for t in parsed_tags:
            call = ToolCall(
                tool=self.tools_by_name[t.tag],
                caller=caller,
                args=(t.content,),
                kwargs={attr[0]: attr[1] for attr in t.attrs},
            )
            tool_calls.append(call)
        return tuple(tool_calls)

    def split_tags(self, parse_results: Collection[ParseResult]) -> list[ParseResult]:
        return_list = []
        for pr in parse_results:
            if pr.tag in self.tags_to_split_per_line:
                for line in pr.content.splitlines():
                    return_list.append(
                        ParseResult(tag=pr.tag, attrs=pr.attrs, content=line)
                    )
                continue
            return_list.append(pr)
        return return_list
