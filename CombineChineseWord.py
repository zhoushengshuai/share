# coding = utf-8

__author__ = 'Zhou Shengshuai'
__version__ = '1.0'

import logging
import re

import requests
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}

ZUCI_TERM_URL = 'https://hanyu.baidu.com/zici/s?wd={character}组词&cf=zuci&ptype=term'
ZICI_REGEXP = r'^\/s\?wd=.*ptype=zici$'
ZICI_COUNT = 10
ZICI_SEPARATOR = '----------{character}----------'


class CombineChineseWord(object):
    def __init__(self):
        logging.basicConfig(format='%(asctime)s %(filename)s[line:%(lineno)d]%(levelname)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p', level=logging.INFO)

    def format_word(self, zici, pinyin):
        formatted_zici = zici.text.strip()
        formatted_pinyin = pinyin.text.strip()
        logging.info('{0}: {1}'.format(formatted_zici, formatted_pinyin))

    def combine_word(self, character):
        logging.debug(ZUCI_TERM_URL.format(character=character))
        logging.info(ZICI_SEPARATOR.format(character=character))
        response = requests.get(ZUCI_TERM_URL.format(character=character), headers=HEADERS, timeout=30)
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        words = soup.find_all(class_='poem-list-item')
        for word in words[:ZICI_COUNT]:
            zici = word.find('a', href=re.compile(ZICI_REGEXP))
            pinyin = word.find(id='pinyin')
            self.format_word(zici, pinyin)


if __name__ == '__main__':
    combineChineseWord = CombineChineseWord()
    characters = input('小孩，请输入生字：')
    for character in characters:
        logging.debug('生字：{0}'.format(character))
        combineChineseWord.combine_word(character)
