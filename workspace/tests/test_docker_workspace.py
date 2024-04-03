import os
import shutil
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
        self.assertEqual("moi", result.content)
        self.assertEqual(0, result.status)

    def test_maintain_state(self):
        self.workspace.run_command("mkdir /test-dir")
        self.workspace.run_command("cd /test-dir")
        result = self.workspace.run_command("pwd")
        self.assertEqual("/test-dir", result.content)
        self.assertEqual(0, result.status)

    def test_command_failure(self):
        result = self.workspace.run_command("9afhpash9aew")
        self.assertNotEqual(0, result.status)

    def test_file_creation(self):
        self.workspace.run_command('echo "This is a test file" > test')
        result = self.workspace.run_command("cat test")
        self.assertEqual("This is a test file", result.content)

    def test_save_file(self):
        text_content = "This is the text content to be saved inside the container. It can include \"quotes\", 'single quotes', `backticks`, and other special characters."
        filename = "/save-file-function-test-file.txt"
        result = self.workspace.save_file(
            content=text_content, file_absolute_path=filename
        )
        self.assertEqual(0, result.status)
        result = self.workspace.run_command(f"cat {filename}")
        self.assertEqual(0, result.status)
        self.assertEqual(text_content, result.content)

    def tearDown(self):
        self.workspace.cleanup()
        shutil.rmtree(self.workspace_dir)
