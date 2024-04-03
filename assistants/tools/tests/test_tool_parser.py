from unittest import TestCase
from unittest.mock import MagicMock, create_autospec

from assistants.tools import ToolParser
from assistants.tools.tag_parser import ParseResult
from workspace import Workspace


class TestToolParser(TestCase):
    def test_split_tags(self):
        prs = [ParseResult(tag="shell", attrs=tuple(), content="cd /root/\nls -l")]
        tp = ToolParser(workspace=create_autospec(Workspace), message_bus=MagicMock())
        result = tp.split_tags(prs)
        self.assertEqual(2, len(result))
        expected = [
            ParseResult(tag="shell", attrs=tuple(), content="cd /root/"),
            ParseResult(tag="shell", attrs=tuple(), content="ls -l"),
        ]
        self.assertEqual(expected, result)

    def test_dont_split_tags(self):
        prs = [ParseResult(tag="message", attrs=tuple(), content="cd /root/\nls -l")]
        tp = ToolParser(workspace=create_autospec(Workspace), message_bus=MagicMock())
        result = tp.split_tags(prs)
        self.assertEqual(1, len(result))
        expected = [
            ParseResult(tag="message", attrs=tuple(), content="cd /root/\nls -l")
        ]
        self.assertEqual(expected, result)
