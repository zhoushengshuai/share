# coding = utf-8

__author__ = 'Zhou Shengshuai'
__version__ = '1.0'

import logging
import os
from random import choice
from random import randint

import requests
from bs4 import BeautifulSoup
from pyquery import PyQuery
from retrying import retry

PROXY_POOL_URL = 'http://www.66ip.cn/{page}.html'
PROXY_POOL_PAGES = 3

HEADERS = {'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}
HTTP_PROXY, HTTPS_PROXY = 'http://{0}', 'https://{0}'

DOUBAN_MOVIE_COMMENTS_START_URL = 'https://movie.douban.com/subject/25917973/comments'
DOUBAN_MOVIE_COMMENTS_REQUEST_DATA = {'status': 'P'}

DOUBAN_LOGIN_URL = 'http://accounts.douban.com/login'
DOUBAN_LOGIN_ACCOUNT1 = ('254392398@qq.com', 'Shuai@903')
DOUBAN_LOGIN_ACCOUNT2 = ('zhoushengshuai2007@163.com', 'Shuai@903')

DOUBAN_MOVIE_COMMENTS_FILE = r'c:/study/output/douban_movie_comments_25917973.txt'


class DouBanMovieCommentsCrawler(object):
    def __init__(self):
        logging.basicConfig(format='%(asctime)s %(filename)s[line:%(lineno)d]%(levelname)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p', level=logging.INFO)
        self.check_clean_file(DOUBAN_MOVIE_COMMENTS_FILE)
        self.session = requests.session()

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

    # 从（免费）代理池网站上爬取代理
    def crawl_proxy_pool(self, url, pages):
        urls = [url.format(page=page) for page in range(1, pages + 1)]
        proxies = []
        for url in urls:
            html = self.get_response_html('get', url)
            if html:
                doc = PyQuery(html)
                trs = doc('.containerbox table tr:gt(0)').items()
                for tr in trs:
                    ip = tr.find('td:nth-child(1)').text()
                    port = tr.find('td:nth-child(2)').text()
                    proxy = ':'.join([ip, port])
                    logging.info('Crawl proxy [{0}] from proxy pool url [{1}]'.format(proxy, url))
                    proxies.append(proxy)
        return proxies

    # 从代理池中随机得到一个代理，以此代理爬取目标网站数据（防反爬虫手段之一）
    def get_random_proxy(self, proxies):
        proxy = choice(proxies)
        logging.info('Choose random proxy [{0}]'.format(proxy))
        return {'http': HTTP_PROXY.format(proxy), 'https': HTTPS_PROXY.format(proxy)}

    # 随机获取注册的多个豆瓣帐户，以此登录豆瓣（防反爬虫手段之一）
    @retry(stop_max_attempt_number=3, stop_max_delay=30000, wait_random_min=3000, wait_random_max=10000)
    def login_to_douban(self, proxies):
        douban_login_account = (DOUBAN_LOGIN_ACCOUNT1, DOUBAN_LOGIN_ACCOUNT2)[randint(0, 1)]
        logging.info('Login to douban with account {0}'.format(douban_login_account))
        form_data = {
            'redir': DOUBAN_MOVIE_COMMENTS_START_URL,
            'form_email': douban_login_account[0],
            'form_password': douban_login_account[1],
            'login': u'登录'
        }
        try:
            self.session.request('post', DOUBAN_LOGIN_URL, data=form_data, headers=HEADERS)
        except:
            self.session.request('post', DOUBAN_LOGIN_URL, data=form_data, headers=HEADERS, proxies=self.get_random_proxy(proxies))

    # 获取URL请求的响应数据
    def get_response_html(self, method, url, data=None, options_headers={}, proxies={}):
        logging.info('It is ongoing to crawl url [{0}]'.format(url))
        try:
            response = self.session.request(method, url, data=data, headers=dict(HEADERS, **options_headers), proxies=proxies)
            logging.info('Finished to crawl url [{0}] with status calculation [{0}]'.format(url, response.status_code))
            if response.status_code == 200:
                return response.text
        except ConnectionError:
            logging.info('Failed to crawl url [{0}] with connection error [{1}]'.format(url, response.reason))
            return None

    # 根据异常情况是否随机选择代理，并获取URL请求的响应数据
    @retry(stop_max_attempt_number=3, stop_max_delay=30000, wait_random_min=3000, wait_random_max=10000)
    def get_short_comments_html(self, url, proxies):
        try:
            html = self.get_response_html('post', url, data=DOUBAN_MOVIE_COMMENTS_REQUEST_DATA, proxies={})
        except:
            html = self.get_response_html('post', url, data=DOUBAN_MOVIE_COMMENTS_REQUEST_DATA, proxies=self.get_random_proxy(proxies))
        if html:
            return html
        else:
            self.login_to_douban(proxies)
            raise Exception('HTTP(S) Connection Exception')

    # 获取下一页的URL地址
    def get_next_url(self, soup):
        paginator_soup = soup.find(id='paginator')
        try:
            href_soup = paginator_soup.find_all(name='a')[2]
        except IndexError:
            href_soup = paginator_soup.find_all(name='a')[0]
        url = DOUBAN_MOVIE_COMMENTS_START_URL + href_soup['href']
        logging.info('Next page url [{0}]'.format(url))
        return url

    # 翻页递归爬取短评数据
    def crawl_short_comments(self, url, proxies):
        html = self.get_short_comments_html(url, proxies)
        soup = BeautifulSoup(html, 'lxml')
        short_comments = soup.find_all('span', {'class': 'short'})
        one_page_short_comments = []
        for short_comment in short_comments:
            short_comment_text = short_comment.text
            one_page_short_comments.append(short_comment_text)
            logging.info('Short Comment: \n{0}'.format(short_comment_text))
        self.write_content_to_file('\n\n'.join(one_page_short_comments), DOUBAN_MOVIE_COMMENTS_FILE)
        logging.info('========================================================Next Page========================================================')
        next_url = self.get_next_url(soup)
        next_url and self.crawl_short_comments(next_url, proxies)


if __name__ == '__main__':
    douBanMovieCommentsCrawler = DouBanMovieCommentsCrawler()
    proxies = douBanMovieCommentsCrawler.crawl_proxy_pool(PROXY_POOL_URL, PROXY_POOL_PAGES)
    douBanMovieCommentsCrawler.crawl_short_comments(DOUBAN_MOVIE_COMMENTS_START_URL, proxies)
