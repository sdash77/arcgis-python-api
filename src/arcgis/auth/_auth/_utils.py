from __future__ import annotations
import re
import urllib.parse as urllib_parse
from functools import lru_cache

__all__ = ["parse_url", "_split_username", "assemble_url"]


@lru_cache(maxsize=255)
def parse_url(url: str) -> object:
    """
    Parses a URL string into it's pieces.

    :returns: Named Tuple
    """
    return urllib_parse.urlparse(url)


@lru_cache(maxsize=255)
def assemble_url(parsed: object) -> str:
    """
    creates the URL from a parsed URL
    """
    if parsed.port:
        netloc: str = parsed.netloc.split(":")[0]
        server_url = (
            f'{parsed.scheme}://{netloc}:{parsed.port}/{parsed.path[1:].split("/")[0]}'
        )
    else:
        server_url = (
            f'{parsed.scheme}://{parsed.netloc}/{parsed.path[1:].split("/")[0]}'
        )
    return server_url


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
