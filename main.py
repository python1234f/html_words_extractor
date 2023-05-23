"""
Assumptions:

    Load html all at once and keep it in memory.

    Complexity O(n) - go through entire html once

    Order of tags is not known (

    Only content from body is considered, but script and style tags from body are excluded.
    More tags can be excluded, this is parametrizable.
    Everything between opening <> and closing </> of any excluded tag is ignored

    No Javascript/PHP will be executed. So nothing can be different in HTML from the original HTML returned from server.
    Text within the <script> or <style> (or any other excluded tags) is not considered, even if it looks human-readable

    Because there may be many words, and many languages (Polish has 150-200k words since it has cases),
    the object that contains word count will be indexed based on first, second, third letter etc.

    Word count is kept in memory.

    requests library is used for fetching html,
    implementing http redirect and other logic on sockets would take too much time

"""
import requests


class Tag:

    def __init__(self, tagType):
        self.tagType = tagType

        self.openingTagOpened = False
        self.openingTagClosed = False

        self.closingTagOpened = False
        self.closingTagClosed = False

        self.position = 0

    def handle_letter(self, letter):
        if letter == self.tagType[self.position]:
            self.position += 1
            if self.position == len(self.tagType):
                self.close_tag()

    def close_tag(self):
        if not self.openingTagClosed:
            self.openingTagClosed = True
        else:
            self.closingTagClosed = True




class Extractor:

    excluded_tags = ["script", "style"]

    def __init__(self, url):

        self.html = None
        self.url = url

        self.load_html()

        self.body_tag = Tag("body")

        self.current_child_tag = None

    def load_html(self):
        # self.html = requests.get(self.url).text
        with open('mock_data') as f:
            self.html = f.read()

    def run(self):

        bodyStartsAt = None
        for index, char in enumerate(self.html):
            if not self.body_tag.openingTagClosed:
                print(1)
            elif self.body_tag.closingTagClosed:
                print(1)

        # split loops so if's evaluated less times



extractor = Extractor("https://onet.pl")
extractor.run()