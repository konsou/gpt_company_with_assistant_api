import message_bus
import workspace
from assistants.tag_parser import ExecuteTagParser, MessageTagParser


class BaseAssistant:
    def __init__(
        self,
        model: str,
        name: str,
        role: str,
        instructions: str,
        message_bus: message_bus.MessageBus,
        workspace: workspace.Workspace,
    ):
        self.model = model
        self.name = name
        self.role = role
        self.instructions = f"Your role is {role}. {instructions}"
        self.message_bus = message_bus
        self.message_bus.subscribe(self.name, self.handle_message)
        self.workspace = workspace
        self._execute_tag_parser = ExecuteTagParser()
        self._message_tag_parser = MessageTagParser()

    def handle_message(self, message: message_bus.Message):
        raise NotImplementedError

    def run_command(self, command: str):
        return self.workspace.run_command(command)

    def parse_execute_commands(self, text: str) -> list[str]:
        self._execute_tag_parser.reset()
        self._execute_tag_parser.feed(text)
        self._execute_tag_parser.close()
        return [t for t in self._execute_tag_parser.texts if t.strip()]

    def parse_message_commands(self, text: str) -> list[message_bus.Message]:
        # TODO: reduce repetition
        self._message_tag_parser.reset()
        self._message_tag_parser.feed(text)
        self._message_tag_parser.close()
        return [
            message_bus.Message(
                sender=self.name,
                recipient=m.recipient,
                content=m.content,
            )
            for m in self._message_tag_parser.messages
            if m.recipient.strip() and m.content.strip()
        ]
