from unittest import TestCase

from assistants.tools.tag_parser import ToolTagParser


class TestToolTagParser(TestCase):
    def test_smaller_than(self):
        text = "<save>1 < 2</save>"
        tag_parser = ToolTagParser(tags=("save",))
        tag_parser.feed(text)
        self.assertEqual("1 < 2", tag_parser.parsed_tags[0].content)
