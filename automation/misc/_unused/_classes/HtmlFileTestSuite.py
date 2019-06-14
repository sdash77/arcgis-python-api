import os
import unittest
import logging
log = logging.getLogger()

import xmlrunner

from automation._classes.HtmlImgLinkParser import HtmlImgLinkParser
from automation._classes.TestHtmlMatch import TestHtmlMatch

class LogDebugStream:
    """Used to send xmlrunner's output to log.debug"""
    def writeln(self, msg):
        log.debug(msg+"\n")

    def write(self, msg):
        log.debug(msg)

class HtmlFileTestSuite:
    """Given an html file, find every img and link in the file, and test
    that it is a valid url that can be connected to, doesn't 404, etc.
    """
    def __init__(self, html_file_path, tests_output_dir, dev_website_server,
                 runner=xmlrunner.XMLTestRunner):
        """html_file_path is the html file to test
        tests_output_dir is the output dir where all .xml files are put
        dev_website_server is the base server used to resolve relative URLs
        """
        self.html_file_path = html_file_path
        self.parser = HtmlImgLinkParser(html_file_path)
        self.tests_output_dir = tests_output_dir
        self.dev_website_server = dev_website_server
        self.runner = runner(output=tests_output_dir, stream=LogDebugStream())
        self.suite = unittest.TestSuite()

    def run_tests(self):
        """After instantiating the object, run this to run all the tests"""
        self._discover_all_tests()
        self._run_all_discovered_tests()

    def _discover_all_tests(self):
        """Find every image and url in the html page, add to self.suite"""
        self._discover_img_tests()
        self._discover_href_tests() 

    def _discover_img_tests(self):
        """Create a test for each <img> url in the html file"""
        for img in self.parser.imgs:
            if "data:" in img.url:
                # <img> that are embedded as data in the html
                basename = os.path.basename(img.html_file_path)
                filename = os.path.splitext(basename)[0]
                self.suite.addTest(self._PassTestCaseClass("Found embedded "\
                    "'data:' <img> tag in file {filename} at line {line}, "
                    "char {char}. Passing.".format(filename = filename,
                                                   line = img.line_number,
                                                   char = img.char_number)))
                continue
            if img.url.startswith("/"):
                # Relative paths of images hosted by the dev_site
                img.url = self.dev_website_server + img.url 
            self.suite.addTest(self._TestHtmlMatchClass(img,
                                                        check_https=True))

    def _discover_href_tests(self):
        """Create a test for each <href> tag in the html file"""
        for href in self.parser.hrefs:
            if href.url.startswith("#"):
                self.suite.addTest(self._PassTestCaseClass("Found "\
                    "fragment identifier {}. Auto-passing".format(href.url)))
                continue
            if href.url.startswith("/"):
                # Relative paths of images hosted by the dev_site
                href.url = self.dev_website_server + href.url 
            self.suite.addTest(self._TestHtmlMatchClass(href,
                                                        check_https=False))

    def _PassTestCaseClass(self, msg):
        """returns an instance of auto-passed test w/ message `msg`"""
        class PassTestCase(unittest.TestCase):
            def runTest(self):
                print(msg)
                log.debug(msg)
        return PassTestCase()

    def _TestHtmlMatchClass(self, *args, **kwargs):
        """returns an instance of TestHtmlMatch(*args), except that the class 
        name is renamed to the filename (no extension) in self.html_file_path
        """
        file_name = os.path.splitext(os.path.basename(self.html_file_path))[0]
        RenamedTest = TestHtmlMatch.get_renamed_class(class_name=file_name)
        return RenamedTest(*args, **kwargs)

    def _run_all_discovered_tests(self):
        self.runner.run(self.suite)

