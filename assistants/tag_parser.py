from html.parser import HTMLParser


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
