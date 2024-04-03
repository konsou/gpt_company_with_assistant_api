import os
import tempfile
from unittest import TestCase
from unittest.mock import patch

import workspace.docker_workspace


class TestDockerWorkspace(TestCase):
    @patch("workspace.docker_workspace.WORKSPACE_DIR", tempfile.mkdtemp())
    def setUp(self):
        # TODO: workspace dir seems to be reused?
        self.workspace = workspace.docker_workspace.DockerWorkspace()
        self.workspace_dir = workspace.docker_workspace.WORKSPACE_DIR

    def test_run_one_command(self):
        result = self.workspace.run_command("echo moi")
        self.assertEqual(result.content, "moi")
        self.assertEqual(result.status, 0)

    def test_maintain_state(self):
        self.workspace.run_command("mkdir /test-dir")
        self.workspace.run_command("cd /test-dir")
        result = self.workspace.run_command("pwd")
        self.assertEqual(result.content, "/test-dir")
        self.assertEqual(result.status, 0)

    def test_command_failure(self):
        result = self.workspace.run_command("9afhpash9aew")
        self.assertNotEquals(result.status, 0)

    def tearDown(self):
        self.workspace.cleanup()
        os.removedirs(self.workspace_dir)
