from main import Extractor


def read_test_data(filename):
    with open(f"test_data/{filename}") as f:
        return f.read()


def test1():
    html = read_test_data("test1")
    extractor = Extractor(url=None, html=html)
    extractor.run()
    words = extractor.words

    expected_words = ["YES0", "YES1", "YES2", "YES3", "YES4", "YES5", "YES6", "YES7", "YES8", "YES9",
                          "YES11", "YES22", "YES33", "YES111", "YES222", "YES333"]
    for expected_word in expected_words:
        assert words[expected_word] == 1
    assert words["YES"] == 3
    # No other words in words object
    assert sorted([i for i in words.keys()]) == sorted([i for i in expected_words + ["YES"]])

    top_ten = {key: extractor.words[key] for key in reversed(sorted(extractor.words, key=extractor.words.get)[-10:])}
    top_ten = "".join([f"{word}: {count}\n" for word, count in top_ten.items()])

    assert top_ten == """YES: 3
YES9: 1
YES8: 1
YES7: 1
YES6: 1
YES5: 1
YES4: 1
YES3: 1
YES2: 1
YES1: 1
"""


if __name__ == "__main__":
    tests = [test1]
    for index, test in enumerate(tests):
        try:
            test()
            print(f"Test {index} passed !")
        except Exception as e:
            print(f"Test {index} failed with Exception: {e}")