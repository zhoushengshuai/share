# coding = utf-8

__author__ = 'Zhou Shengshuai'
__version__ = '1.0'

import logging
import os
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

DOUBAN_MOVIE_COMMENTS_FILE = r'c:/study/output/douban_movie_comments_25917973.txt'
DOUBAN_MOVIE_COMMENTS_URL = 'https://movie.douban.com/subject/25917973/comments?status=P'
DOUBAN_MOVIE_COMMENTS_XPATH = '//div[@id="comments"]/div[{index}]/div[@class="comment"]/p/span[@class="short"]'
DOUBAN_MOVIE_ONE_PAGE_COMMENTS_COUNT = 20

DOUBAN_LOGIN_XPATH = '//a[@class="nav-login" and contains(@href, "https://accounts.douban.com/passport/login") and contains(text(), "登录/注册")]'
DOUBAN_PASSWORD_LOGIN_XPATH = '//li[@class="account-tab-account" and contains(text(), "密码登录")]'

DOUBAN_USERNAME_INPUT_XPATH, DOUBAN_USERNAME = '//input[@id="username" and @class="account-form-input" and @placeholder="手机号 / 邮箱"]', '254392398@qq.com'
DOUBAN_PASSWORD_INPUT_XPATH, DOUBAN_PASSWORD = '//input[@id="password" and @class="account-form-input password" and @placeholder="密码"]', 'Shuai@903'
DOUBAN_LOGIN_BUTTON_XPATH = '//a[@class="btn btn-account btn-active" and contains(text(), "登录豆瓣")]'

DOUBAN_MOVIE_NEXT_PAGE_XPATH = '//div[@id="paginator"]/a[contains(text(), "后页")]'


class DouBanMovieCommentsSpider(object):
    def __init__(self):
        logging.basicConfig(format='%(asctime)s %(filename)s[line:%(lineno)d]%(levelname)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p', level=logging.INFO)
        self.check_clean_file(DOUBAN_MOVIE_COMMENTS_FILE)
        try:
            self.driver = webdriver.Firefox()
        except WebDriverException:
            self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(15)
        self.driver.maximize_window()

    # 检查文件，如果其目录不存在，则创建目录；如果文件存在，则删除清空文件
    def check_clean_file(self, file):
        if not os.path.exists(file):
            # 如果文件不存在，继续检查其目录，如果目录不存在，则创建目录
            self.check_make_directory(os.path.dirname(file))
        else:
            os.remove(file)

    # 检查目录，如果目录不存在，则创建目录
    def check_make_directory(self, directory):
        if not os.path.exists(directory):
            logging.warning('The file {0} does not exist, will make its directory.'.format(directory))
            os.makedirs(directory)

    # 写（追加）内容到文件
    def write_content_to_file(self, content, file):
        with open(file, 'a', encoding='utf-8') as handler:
            handler.write(content)

    # 登录豆瓣
    def login_to_douban(self, url):
        self.driver.get(url)
        WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, DOUBAN_LOGIN_XPATH))).click()
        WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, DOUBAN_PASSWORD_LOGIN_XPATH))).click()
        WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.XPATH, DOUBAN_USERNAME_INPUT_XPATH))).send_keys(DOUBAN_USERNAME)
        WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, DOUBAN_PASSWORD_INPUT_XPATH))).send_keys(DOUBAN_PASSWORD)
        WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, DOUBAN_LOGIN_BUTTON_XPATH))).click()

    # 退出豆瓣
    def quit_douban(self):
        self.driver.quit()

    # 写短评到文件
    def write_short_comments(self):
        one_page_short_comments = []
        for index in range(1, DOUBAN_MOVIE_ONE_PAGE_COMMENTS_COUNT):
            short_comment_element = WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.XPATH, DOUBAN_MOVIE_COMMENTS_XPATH.format(index=index))))
            short_comment_text = short_comment_element.text
            one_page_short_comments.append(short_comment_text)
            logging.info('Short Comment: \n{0}'.format(short_comment_text))
            sleep(1)
        self.write_content_to_file('\n'.join(one_page_short_comments), DOUBAN_MOVIE_COMMENTS_FILE)

    # 翻页递归爬取短评数据
    def crawl_short_comments(self):
        self.write_short_comments()
        try:
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, DOUBAN_MOVIE_NEXT_PAGE_XPATH))).click()
            sleep(3)
            self.crawl_short_comments()
        except TimeoutException:
            self.quit_douban()

    # 爬取短评数据入口
    def main(self):
        self.login_to_douban(DOUBAN_MOVIE_COMMENTS_URL)
        self.crawl_short_comments()


if __name__ == '__main__':
    douBanMovieCommentsSpider = DouBanMovieCommentsSpider()
    douBanMovieCommentsSpider.main()
