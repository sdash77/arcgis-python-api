"""Helper parser classes for run_dev_site_tests.py"""
from html.parser import HTMLParser
from collections import namedtuple

class HtmlMatch: 
    """The object that contains all needed info from a "match" in the html"""
    def __init__(self, html_file_path, url, line_number, char_number):
        self.html_file_path = html_file_path
        self.url = url
        self.line_number = line_number
        self.char_number = char_number

class HtmlImage(HtmlMatch):
    pass

class HtmlLink(HtmlMatch):
    pass

class HtmlImgLinkParser:
    """Given 'html_file_path', open that file, and parse all img/links. Use:
    parser = HtmlImgLinkParser("/some/path")
    parser.imgs #Contains a collection of 'HtmlImage's of all found images
    parser.links #Contains a collection of 'HtmlLink's of all found links
    """
    def __init__(self, html_file_path, *args, **kwargs):
        self.html_file_path = html_file_path
        self._parser = _HTMLParser(self.html_file_path, *args, **kwargs)
        self.imgs = self._parser.imgs
        self.hrefs = self._parser.hrefs
        self._parser.feed(open(html_file_path, "r", encoding="utf8").read())

class _HTMLParser(HTMLParser):
    """Child class of HTMLParser that implements img/href parsing logic"""
    def __init__(self, html_file_path, *args, **kwargs):
        self.html_file_path = html_file_path
        self.imgs = []
        self.hrefs = []
        super().__init__(*args, **kwargs)

    def handle_starttag(self, tag, attrs):
        if tag=="img":
            #For all <img> tags
            self.imgs.append(
                HtmlImage(html_file_path = self.html_file_path,
                          url = dict(attrs)["src"],
                          line_number = self.getpos()[0],
                          char_number = self.getpos()[1]))
        elif tag=="a":
            for (key, value) in attrs:
                if key == "href":
                    #For all <href> tags
                    self.hrefs.append(
                        HtmlLink(html_file_path = self.html_file_path,
                                 url = value,
                                 line_number = self.getpos()[0],
                                 char_number = self.getpos()[1]))

