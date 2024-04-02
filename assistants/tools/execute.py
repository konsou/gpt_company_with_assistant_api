from assistants.tools.types import Tool
from workspace import Workspace


class Execute(Tool):
    def __init__(self, workspace: Workspace):
        self._workspace = workspace

    def function(self, command: str) -> str:
        return self._workspace.run_command(command).content
