import re
import urllib.parse as urllib_parse
from functools import lru_cache

__all__ = ['parse_url', '_split_username']


@lru_cache(maxsize=255)
def parse_url(url: str) -> object:
    """
    Parses a URL string into it's pieces.

    :returns: Named Tuple
    """
    return urllib_parse.urlparse(url)


@lru_cache(maxsize=255)
def _split_username(username: str) -> list[str]:
    regex = r"(\S*)?(@|#|//|\\\\|(?<!/)/(?!/)|\\)(\S*)"
    matches = re.finditer(regex, username, re.IGNORECASE | re.DOTALL)
    tokens = []
    for match in matches:
        for group in match.groups():
            tokens.append(group)

    if tokens[1] in ["//", "\\", "/"]:
        uname = tokens[2]
        dom = tokens[0]
    elif tokens[1] == "@":
        uname = tokens[0]
        dom = tokens[2]

    return [uname, dom]
