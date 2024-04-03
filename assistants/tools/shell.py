from assistants.tools.abc import Tool
from workspace import Workspace


class Shell(Tool):
    def __init__(self, workspace: Workspace):
        self._workspace = workspace

    def function(self, command: str, *args, **kwargs) -> str:
        result = self._workspace.run_command(command)
        return result.content
        # Status not implemented yet
        # return f"{result.content}\nCommand finished with exit code {result.status}"
