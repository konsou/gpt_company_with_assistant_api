from html.parser import HTMLParser
from typing import NamedTuple, Collection, Optional

Attr = tuple[str, str | None]


class ParseResult(NamedTuple):
    tag: str
    attrs: tuple[Attr]
    content: str


class ToolTagParser(HTMLParser):
    def __init__(self, tags: Collection[str]):
        super().__init__()
        self.valid_tags = tags
        self.active_tag: Optional[str] = None
        self.attrs: tuple[Attr] = tuple()
        self.parsed_tags: list[ParseResult] = []
        self._data: str = ""

    def reset(self):
        super().reset()
        self.active_tag: Optional[str] = None
        self.attrs: tuple[Attr] = tuple()
        self.parsed_tags: list[ParseResult] = []
        self._data = ""

    def handle_starttag(self, tag, attrs):
        if tag in self.valid_tags:
            self.active_tag = tag
            self.attrs = tuple(attrs)

    def handle_endtag(self, tag):
        if tag in self.valid_tags:
            self.parsed_tags.append(
                ParseResult(tag=self.active_tag, attrs=self.attrs, content=self._data)
            )
            self.active_tag = None
            self._data = ""

    def handle_data(self, data):
        if self.active_tag is not None:
            self._data = f"{self._data}{data}"
