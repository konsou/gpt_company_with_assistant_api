from unittest import TestCase

from assistants.tools.tag_parser import ToolTagParser


class TestToolTagParser(TestCase):
    def test_smaller_than(self):
        text = "<save>1 < 2</save>"
        tag_parser = ToolTagParser(tags=("save",))
        tag_parser.feed(text)
        self.assertEqual("1 < 2", tag_parser.parsed_tags[0].content)

    def test_greater_than(self):
        text = "<save>1 > 2</save>"
        tag_parser = ToolTagParser(tags=("save",))
        tag_parser.feed(text)
        self.assertEqual("1 > 2", tag_parser.parsed_tags[0].content)

    def test_multiline(self):
        text = (
            "Hello! Let's save multiple lines: <save>\n"
            "def func(arg: int) -> str:\n"
            "    s = str(arg)\n"
            "    return s\n"
            "</save>"
        )
        tag_parser = ToolTagParser(tags=("save",))
        tag_parser.feed(text)
        expected_parse_content = (
            "\ndef func(arg: int) -> str:\n    s = str(arg)\n    return s\n"
        )
        self.assertEqual(expected_parse_content, tag_parser.parsed_tags[0].content)
