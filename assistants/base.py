import message_bus
import workspace


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

    def handle_message(self, message: message_bus.Message):
        raise NotImplementedError

    def run_command(self, command: str):
        return self.workspace.run_command(command)
