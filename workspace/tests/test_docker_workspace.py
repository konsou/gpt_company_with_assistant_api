import os
import tempfile
from unittest import TestCase
from unittest.mock import patch

import workspace.docker_workspace


class TestDockerWorkspace(TestCase):
    @patch("workspace.docker_workspace.WORKSPACE_DIR", tempfile.mkdtemp())
    def test_run_one_command(self):
        ws = workspace.docker_workspace.DockerWorkspace()
        workspace_dir = workspace.docker_workspace.WORKSPACE_DIR
        print(workspace_dir)
        result = ws.run_command("echo moi")
        self.assertEqual(result.content, "moi")
        self.assertEqual(result.status, 0)
        ws.cleanup()
        os.removedirs(workspace_dir)

    @patch("workspace.docker_workspace.WORKSPACE_DIR", tempfile.mkdtemp())
    def test_maintain_state(self):
        ws = workspace.docker_workspace.DockerWorkspace()
        workspace_dir = workspace.docker_workspace.WORKSPACE_DIR
        print(workspace_dir)
        ws.run_command("mkdir /test-dir")
        ws.run_command("cd /test-dir")
        result = ws.run_command("pwd")
        self.assertEqual(result.content, "/test-dir")
        self.assertEqual(result.status, 0)
        ws.cleanup()
        os.removedirs(workspace_dir)
