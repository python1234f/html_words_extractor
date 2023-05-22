"""
Assumptions:

    Load html all at once and keep it in memory.

    Order of tags is not known (

    Only content from body is considered, but script and style tags from body are excluded.
    More tags can be excluded, this is parametrizable.

    No Javascript/PHP will be executed. So nothing can be different in HTML from the original HTML returned from server.
    Text within the <script> or <style> (or any other excluded tags) is not considered, even if it looks human-readable

    Because there may be many words, and many languages (Polish has 150-200k words since it has cases),
    the object that contains word count will be indexed based on first, second, third letter etc.

    Word count is kept in memory.

    requests library is used for fetching html,
    implementing http redirect and other logic on sockets would take too much time

"""