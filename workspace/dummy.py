from workspace import Workspace
from workspace.base import CommandResult


class DummyWorkspace(Workspace):
    def run_command(self, command: str) -> CommandResult:
        print(f"Faking running command: {command}")
        return CommandResult(status=0, content="Test command succeeded")
