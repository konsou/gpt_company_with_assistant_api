from assistants.tools.execute import Execute
from assistants.tools.tag_parser import ToolTagParser
from assistants.tools.types import Tool, ToolCall
from message_bus import MessageBus
from workspace import Workspace, DummyWorkspace


class ToolParser:
    def __init__(self, workspace: Workspace, message_bus: MessageBus):
        self.workspace = workspace
        self.message_bus = message_bus
        self.all_tools = (Execute(workspace=workspace),)
        self.tools_by_name: dict[str, Tool] = {t.name: t for t in self.all_tools}
        self._parser = ToolTagParser(tags=self.tools_by_name.keys())

    def parse(self, text: str) -> tuple[ToolCall, ...]:
        self._parser.reset()
        self._parser.feed(text)
        self._parser.close()
        parsed_tags = self._parser.parsed_tags
        tool_calls = []
        for t in parsed_tags:
            call = ToolCall(
                tool=self.tools_by_name[t.tag],
                args=(t.content,),
                kwargs={attr[0]: attr[1] for attr in t.attrs},
            )
            tool_calls.append(call)
        return tuple(tool_calls)
