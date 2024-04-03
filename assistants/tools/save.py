from assistants.tools.abc import Tool
from workspace import Workspace


class Save(Tool):
    def __init__(self, workspace: Workspace):
        self._workspace = workspace

    def function(self, content: str, file_absolute_path: str, caller: str) -> str:
        result = self._workspace.save_file(
            content=content, file_absolute_path=file_absolute_path
        )
        return result.content
