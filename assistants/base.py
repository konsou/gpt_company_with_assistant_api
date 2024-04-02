from typing import Optional, Collection, TypedDict, Literal, NotRequired

import message_bus
import workspace

from assistants.tools import ToolParser
from assistants.tools.types import ToolCall


class InternalMessage(TypedDict):
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    name: NotRequired[str]


class BaseAssistant:
    def __init__(
        self,
        name: str,
        role: str,
        instructions: str,
        message_bus: message_bus.MessageBus,
        workspace: workspace.Workspace,
        model: Optional[str] = None,
        models: Optional[list[str]] = None,
    ):
        self.model = model
        self.models = models
        self.name = name
        self.role = role
        self.instructions = f"Your role is {role}. {instructions}"
        self.message_bus = message_bus
        self.message_bus.subscribe(self.name, self.handle_bus_message)
        self.workspace = workspace
        self._tool_parser = ToolParser(workspace=workspace, message_bus=message_bus)

    def handle_bus_message(self, message: message_bus.Message):
        raise NotImplementedError

    def send_message(self, message: message_bus.Message) -> InternalMessage:
        result = self.message_bus.publish(
            message_bus.Message(
                sender=self.name,
                recipient=message.recipient,
                content=message.content,
            )
        )
        content = (
            f"Message successfully sent to {message.recipient}"
            if result
            else f"Failed to send message to {message.recipient}"
        )
        return {"role": "tool", "content": content}

    def parse_tool_calls(self, content: str) -> tuple[ToolCall, ...]:
        result = self._tool_parser.parse(content)
        return result

    def call_tools(self, calls: Collection[ToolCall]):
        raise NotImplementedError
