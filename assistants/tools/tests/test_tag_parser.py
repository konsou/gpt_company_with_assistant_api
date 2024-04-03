from unittest import TestCase

from assistants.tools.tag_parser import ToolTagParser, ParseResult


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

    def test_nested_tags(self):
        text = "<tag1><tag2>Content</tag2></tag1>"
        tag_parser = ToolTagParser(tags=("tag1", "tag2"))
        tag_parser.feed(text)
        # No support for nested tags at the moment - only handle the outermost tag
        self.assertEqual(
            "[ERROR: Nested tags detected]<tag2>Content</tag2>",
            tag_parser.parsed_tags[0].content,
        )
        self.assertEqual("tag1", tag_parser.parsed_tags[0].tag)
