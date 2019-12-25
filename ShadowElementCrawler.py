# coding = utf-8
__author__ = 'shengshuai.zhou@nokia-sbell.com'
__version__ = '1.0'

import logging
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

START_PAGE = 'http://xxx.xxx.xxx.xxx:80'

APP_ROOT_ID = 'app'
APP_ELEMENT_ID = 'app-element'
MAIN_HEADER_CSS = '#header > gr-main-header'
LOGIN_BUTTON_CLASS = '.loginButton'

USERNAME_XPATH, USERNAME = '//input[@id="f_user" and @name="username"]', 'developer1'
PASSWORD_XPATH, PASSWORD = '//input[@id="f_pass" and @name="password"]', '123456'
SIGN_IN_XPATH = '//input[@id="b_signin" and @type="submit" and @value="Sign In"]'


class ShadowElementCrawler(object):
    def __init__(self):
        logging.basicConfig(format='%(asctime)s %(filename)s[line:%(lineno)d]%(levelname)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p', level=logging.INFO)
        try:
            self.driver = webdriver.Chrome()
        except WebDriverException:
            self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(15)
        self.driver.maximize_window()

    def expand_shadow_element(self, element):
        shadow_element = self.driver.execute_script('return arguments[0].shadowRoot', element)
        return shadow_element

    def sign_in_click(self):
        app_root_element = self.expand_shadow_element(self.driver.find_element_by_id(APP_ROOT_ID))
        app_element = self.expand_shadow_element(app_root_element.find_element_by_id(APP_ELEMENT_ID))
        main_header_element = self.expand_shadow_element(app_element.find_element_by_css_selector(MAIN_HEADER_CSS))
        WebDriverWait(main_header_element, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, LOGIN_BUTTON_CLASS))).click()

    def sign_in_input(self, username, password):
        WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.XPATH, USERNAME_XPATH))).send_keys(username)
        WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.XPATH, PASSWORD_XPATH))).send_keys(password)
        WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, SIGN_IN_XPATH))).click()

    def sign_in(self, url, username, password):
        logging.info('Sign in {0} with username [{1}] and password [{2}]'.format(url, username, password))
        self.driver.get(url)
        self.sign_in_click()
        self.sign_in_input(username, password)

    def log_out(self):
        sleep(3)
        self.driver.quit()

    def main(self):
        self.sign_in(START_PAGE, USERNAME, PASSWORD)
        self.log_out()


if __name__ == '__main__':
    shadowElementCrawler = ShadowElementCrawler()
    shadowElementCrawler.main()
