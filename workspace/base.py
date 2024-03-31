from typing import NamedTuple


class CommandResult(NamedTuple):
    status: int
    content: str


class Workspace:
    def run_command(self, command: str) -> CommandResult:
        raise NotImplementedError
