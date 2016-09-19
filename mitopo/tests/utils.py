import unittest

import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class MitopoTestCase(unittest.TestCase):

    def setUp(self):
        self.slow_down = None
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def try_slow_down(self):
        if self.slow_down is not None:
            time.sleep(self.slow_down/1000.0)

    def ensure_absent(self, css_selector):
        self.try_slow_down()
        try:
            self.browser.find_element_by_css_selector(css_selector)
            self.fail("css selector '"+ css_selector + "' is supposed to be absent, but was found")
        except NoSuchElementException:
            pass

    def ensure_present(self, css_selector):
        self.try_slow_down()
        return self.browser.find_element_by_css_selector(css_selector)