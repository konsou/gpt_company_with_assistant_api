from typing import NamedTuple, Protocol


class CommandResult(NamedTuple):
    status: int
    content: str


class Workspace(Protocol):
    def run_command(self, command: str) -> CommandResult: ...

    def save_file(self, content: str, file_absolute_path: str) -> CommandResult: ...
