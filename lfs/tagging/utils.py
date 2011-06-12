import HTMLParser


class SimpleHTMLParser(HTMLParser.HTMLParser):
    """A simple HTML parser to get the plain data.
    """
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.data = ""

    def handle_data(self, data):
        self.data += data
