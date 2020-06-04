# coding = utf-8
__author__ = 'Zhou Shengshuai'
__version__ = '1.0'

import logging
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

REPOSITORY_URL = 'http://127.0.0.1:30317/ui'
REPOSITORY_USERNAME = 'admin'
REPOSITORY_PASSWORD = 'Yh123$%^'

REPOSITORY_USERNAME_XPATH = '//input[@name="username"]'
REPOSITORY_PASSWORD_XPATH = '//input[@name="password"]'
REPOSITORY_LOGIN_XPATH = '//button[@type="submit"]'

REPOSITORY_STARTED_XPATH = '//button[@type="button" and contains(@class, "get-started")]'
REPOSITORY_STARTED_CLOSE_XPATH = '//div[contains(@class, "close-button")]/i[@class="icon-close"]'

REPOSITORY_ADMIN_XPATH = '//div[@class="icons"]/img[@alt="admin"]'
REPOSITORY_VSM1_XPATH = '//span[@class="vsm--link vsm--link_level-1"]/span[contains(text(), "Repositories")]'
REPOSITORY_VSM2_XPATH = '//a[@class="vsm--link vsm--link_level-2"]/span[contains(text(), "Repositories")]'

REPOSITORY_NEW_XPATH = '//a[@class="new-entity ng-scope"]/span[contains(text(), "New Local Repository")]'
REPOSITORY_TYPE_XPATH = '//span[contains(text(), "{package_type}")]'
REPOSITORY_KEY_XPATH = '//input[@id="repoKey-new"]'
REPOSITORY_SAVE_XPATH = '//button[@type="submit" and @id="repository-save-button"]'


class RepositoryCrawler(object):
    def __init__(self, timeout=10):
        logging.basicConfig(format='%(asctime)s %(filename)s[line:%(lineno)d]%(levelname)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p', level=logging.INFO)
        try:
            self.driver = webdriver.Chrome()
        except WebDriverException:
            self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(timeout)
        self.driver.maximize_window()

    def login_repository(self, url, username, password, timeout=10):
        logging.info('repository = {0}, username = {1}, password = {2}'.format(url, username, password))
        self.driver.get(url)
        WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH, REPOSITORY_USERNAME_XPATH))).send_keys(REPOSITORY_USERNAME)
        WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH, REPOSITORY_PASSWORD_XPATH))).send_keys(REPOSITORY_PASSWORD)
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, REPOSITORY_LOGIN_XPATH))).click()

    def start_repository(self, timeout=3):
        try:
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, REPOSITORY_STARTED_XPATH))).click()
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, REPOSITORY_STARTED_CLOSE_XPATH))).click()
        except TimeoutException:
            logging.warning('Maybe the started page is not existent!')

    def enter_repository(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, REPOSITORY_ADMIN_XPATH))).click()
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, REPOSITORY_VSM1_XPATH))).click()
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, REPOSITORY_VSM2_XPATH))).click()

    def new_repository(self, repository_key, package_type='Generic', timeout=10):
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, REPOSITORY_NEW_XPATH))).click()
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, REPOSITORY_TYPE_XPATH.format(package_type=package_type)))).click()
        WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH, REPOSITORY_KEY_XPATH))).send_keys(repository_key)
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, REPOSITORY_SAVE_XPATH))).click()

    def quit_repository(self):
        time.sleep(6)
        self.driver.quit()

    def main(self):
        self.login_repository(url=REPOSITORY_URL, username=REPOSITORY_USERNAME, password=REPOSITORY_PASSWORD)
        self.start_repository()
        self.enter_repository()
        self.new_repository(repository_key='repository_{0}_test'.format(int(time.time())), package_type='Gradle')
        self.quit_repository()


if __name__ == '__main__':
    repositoryCrawler = RepositoryCrawler()
    repositoryCrawler.main()
