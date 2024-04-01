from html.parser import HTMLParser
from typing import NamedTuple


class ExecuteTagParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside_execute = False
        self.texts = []

    def handle_starttag(self, tag, attrs):
        if tag == "execute":
            self.inside_execute = True

    def handle_endtag(self, tag):
        if tag == "execute":
            self.inside_execute = False

    def handle_data(self, data):
        if self.inside_execute:
            self.texts.append(data.strip())


from html.parser import HTMLParser


class TagMessage(NamedTuple):
    recipient: str
    content: str


class MessageTagParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside_message = False
        self.recipient = ""
        self.messages: list[TagMessage] = []

    def handle_starttag(self, tag, attrs):
        if tag == "message":
            self.inside_message = True
            for attr, value in attrs:
                if attr == "recipient":
                    self.recipient = value

    def handle_endtag(self, tag):
        if tag == "message":
            self.inside_message = False

    def handle_data(self, data):
        if self.inside_message:
            self.messages.append(
                TagMessage(recipient=self.recipient, content=data.strip())
            )
