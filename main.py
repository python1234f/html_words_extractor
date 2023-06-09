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

    every occurence of < , followed by optional / for closing tags, followed by any set of characters
    that does not start with space, followed by >
    is considered a xml tag and is not considered - in this exact way

    additionally, there is a set of predefined types of tags (like <style> tags) where additionally to
    ignoring to the tag as described above, the content within the tag is ignored
    this set of excluded tags is parameterizable.

    it is assumed that for excluded tags, such tag will never have a nested child of the same type,
    e.g. no <style> inside of <style>

    it is assumed that body tag is present

    tests are written without any library, as it would be redundant where the main objective is to test the
    correctness of the algorithm, also I have limited time

    No refactoring has been done

"""
import requests
from datetime import datetime
from sys import argv

class Tag:

    def __init__(self, tagType):
        if tagType:
            self.tagType = tagType
        else:
            self.tagType = ""

        self.consideredTagType = ""

        self.openingTagOpened = False
        self.openingTagClosed = False

        self.closingTagOpened = False
        self.closingTagClosed = False

        self.position = 0

        self.appendTagType = True

        # self.wrong = False  # Not sure myself about this

    def handle_letter(self, letter):
        if letter == self.tagType[self.position]:
            self.position += 1
            if self.position == len(self.tagType.strip()):
                self.close_tag()
        else:
            # if other than next expected letter, reset position
            self.position = 0

    def handle_letter_unknown_tag(self, letter):

        if letter == " ":
            # dont append to tagType anymore (class=,id= etc.)
            self.appendTagType = False
        if not self.appendTagType:
            return
        if not self.openingTagClosed:
            self.tagType += letter
        else:
            self.consideredTagType += letter

    def close_tag(self):
        if not self.openingTagClosed:
            self.openingTagClosed = True
        else:
            self.closingTagClosed = True
        self.appendTagType = True

    def __repr__(self):
        return f"{self.tagType}"


class Extractor:

    excluded_tags = ["script", "style"]

    def __init__(self, url, html=None):

        self.html = None
        self.url = url
        if not html:
            self.load_html()
        else:
            self.html = html
        self.body_tag = Tag("body ")
        self.current_child_tag = None
        self.words = {}

    def add_word_old(self, word):
        insert_pointer = self.words
        for index in range(len(word)):
            letter = word[index]
            if letter not in insert_pointer:
                insert_pointer[letter] = {}
            insert_pointer = insert_pointer[letter]
            if index == len(word) - 1:
                if "count" not in insert_pointer:
                    insert_pointer["count"] = 1
                else:
                    insert_pointer["count"] += 1

    def add_word(self, word):
        if word in self.words:
            self.words[word] += 1
        else:
            self.words[word] = 1

    def load_html(self):
        self.html = requests.get(self.url).text
        # with open('mock_data') as f:
        #     self.html = f.read()

    def run(self):

        isNotBodyTag = False
        tagOpen = False

        for index, letter in enumerate(self.html):
            if not tagOpen:
                if letter == "<":
                    tagOpen = True
            else:
                if letter == ">":
                    tagOpen = False
                    isNotBodyTag = False
                    if self.body_tag.openingTagClosed:
                        # we found the index from which to look for readable words
                        index += 1
                        break
                    continue
                if not isNotBodyTag:
                    if self.body_tag.openingTagClosed:
                        # allow all letters until closing >
                        # for example <body class="SomeClass">
                        continue
                    self.body_tag.handle_letter(letter)
                    if self.body_tag.position == 0:
                        isNotBodyTag = True

        # We are within the body. We can start stripping other tags now.
        someTag = Tag(None)
        tagOpen = False
        tagOpenIndex = None
        ignoreTagContent = False

        for index in range(index, len(self.html)):

            letter = self.html[index]

            if ignoreTagContent:
                # only run rest of the loop if maybe current excluded tag is closed
                # we assume one excluded type is not nested inside another excluded tag, where both of same type
                if not tagOpen:
                    if letter != "<":
                        continue
                    else:
                        pass
                else:
                    pass

            if not tagOpen:
                if letter == "<":
                    if word:
                        self.add_word(word)
                        word = ""
                        someTag = Tag(None)
                    tagOpen = True
                    tagOpenIndex = index
                else:
                    if letter == " ":
                        if word:
                            self.add_word(word)
                            word = ""
                            someTag = Tag(None)
                    if letter.isalnum():
                        word += letter
            else:
                if letter == "/":
                    # we assume no nested excluded tags of same type, see notes
                    continue
                elif index - tagOpenIndex == 1 and letter in [" "]:
                    # we are not dealing with a tag here
                    tagOpen = False
                    tagOpenIndex = 0
                    someTag.appendTagType = True
                    continue
                elif letter != ">":

                    someTag.handle_letter_unknown_tag(letter)
                    continue
                else:
                    if someTag.tagType == 'body':
                        # finished :)
                        break
                    someTag.openingTagClosed = True
                    tagOpen = False
                    tagOpenIndex = 0
                    someTag.appendTagType = True

                    if someTag.tagType in self.excluded_tags:
                        if someTag.tagType == someTag.consideredTagType:
                            # we are closing the tag, so let's not ignore content anymore.
                            ignoreTagContent = False
                            someTag = Tag(None)
                        else:
                            ignoreTagContent = True
                    else:
                        someTag = Tag(None)


if __name__ == "__main__":

    url = argv[1]
    extractor = Extractor(url)
    start = datetime.now()
    extractor.run()
    print(datetime.now() - start)
    words = extractor.words
    top_ten = {key: extractor.words[key] for key in reversed(sorted(extractor.words, key=extractor.words.get)[-10:])}
    top_ten = "".join([f"{word}: {count}\n" for word, count in top_ten.items()])
    print(top_ten)
    with open('results.txt', 'w') as f:
        f.write(top_ten)

