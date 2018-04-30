import os
import types
import unittest
import logging
log = logging.getLogger()

import requests

class RenameableClass:
    """Adds a class method to rename the class that inherits from this"""
    @classmethod
    def get_renamed_class(cls, class_name):
        """returns the functional equivalent of the base class, except
        it changes the class name to whatever is specified in `new_class_name`.
        This is called dynamic class creation. (See types.new_class() docs)
        """
        return types.new_class(class_name, (cls,))

class TestHtmlMatch(unittest.TestCase, RenameableClass):
    """The base test case for testing the url in an HtmlMatch object, if
    you can connect to the server at the url, if it returns an OK status code
    """
    def __init__(self, html_match, check_https, base_server="zion", **kwargs):
        """Will 'rewrite' the runTest methodName to ending of the url"""
        self.html_match = html_match
        self.check_https = check_https
        self.base_server = base_server
        url_ending = html_match.url.split("/")[-1]
        url_ending_no_ext = url_ending.split(".")[0]

        #Renames 'runTest' method to the url ending (readability)
        setattr(self, url_ending_no_ext, self.runTest)
        super().__init__(**kwargs, methodName=url_ending_no_ext)

    def runTest(self):
        """The actual test you want to do on the URL"""        
        request = self._request_html_match()
        self._check_status_code(request)
        self._check_https(request)

        #If we're reached here, we've passed
        msg = "URL OK, Passed. {}".format(self._get_html_match_info_str())
        print(msg)
        log.debug(msg)

    def _check_status_code(self, request):
        if request.status_code >= 400:
            #Any code >=400 is a client or server failure
            self.fail("ERR: {} on url. {}"\
                      "".format(request.status_code,
                                self._get_html_match_info_str()))
        if request.status_code >= 300 and request.status_code <= 399:
            #A redirect code might be OK: just skip the test (a 'warning')
            self.skipTest("Received code {} on url. {}"\
                          "".format(request.status_code,
                                    self._get_html_match_info_str()))
    
    def _check_https(self, request):
        if (self.check_https) and \
           ("http:" in self.html_match.url) and \
           (self.base_server not in self.html_match.url):
            # All external links not hosted by base_server should be https
            self.skipTest("url needs to be https! See https://bit.ly/2GYOkes."\
                            " {}".format(self._get_html_match_info_str()))

    def _request_html_match(self):
        try:
            return requests.get(self.html_match.url)
        except Exception as e:
            self.fail("ERR: Got no response on url. {}"\
                       "".format(self._get_html_match_info_str()))

    def _get_html_match_info_str(self):
        filename = os.path.basename(self.html_match.html_file_path)
        return "File {filename} referenced url '{url}' at line {line}, char "\
                "{char}".format(filename = filename,
                                url = self.html_match.url,
                                line = self.html_match.line_number,
                                char = self.html_match.char_number)

