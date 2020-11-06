# -*- coding: UTF-8 -*-

__author__ = 'Zhou Shengshuai'
__version__ = '1.0'

import logging
import os

import pandas

WORK_DIR = os.path.join(os.path.dirname(__file__))
LOG_FILE = os.path.join(WORK_DIR, 'result.log')
OIB_DB_DIR = os.path.join(WORK_DIR, 'DB')
OIB_NODB_DIR = os.path.join(WORK_DIR, 'noDB')
EXCEL_SUFFIX = r'.xls'
SEPARATOR_LINE = '--------------------------------------------------------------------------------'
KEYWORDS = ['MASTER', 'SLAVE', 'WHITELIST', 'BLACKLIST']


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt='%(asctime)s %(filename)s[line:%(lineno)d]%(levelname)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p')
    fileHandler = logging.FileHandler(filename=LOG_FILE, mode='w')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    return logger


LOGGER = get_logger('HealthCheckKeyword')


def check_path(path):
    LOGGER.debug('Check path {0}'.format(path))
    if not os.path.exists(path): raise AssertionError('Not found path {0}'.format(path))


def get_files(directory):
    for root, directories, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(EXCEL_SUFFIX): yield os.path.join(root, file)
        for directory in directories:
            get_files(directory)


def parse_excel(file, sheet, columns):
    LOGGER.debug('Parse columns {0} under sheet [{1}] in excel {2}'.format(columns, sheet, file))
    contents = []
    with pandas.ExcelFile(file) as xls:
        if sheet in xls.sheet_names:
            data = pandas.read_excel(file, sheet_name=sheet)
            dataFrame = pandas.DataFrame(data=data, columns=columns)
            contents = dataFrame.dropna().values.tolist()
            LOGGER.debug(contents)
            LOGGER.debug(SEPARATOR_LINE)
    return contents


def parse_excels(files, sheet, columns):
    allContents = []
    for file in files:
        contents = parse_excel(file=file, sheet=sheet, columns=columns)
        contents and allContents.append(contents)
    return allContents


def find_keyword(columns, contents, keywords):
    LOGGER.debug('Find keywords {0} for columns {1}'.format(keywords, columns))
    for content in contents:
        if len(columns) != len(content): raise AssertionError('Not match between columns and contents')
        columnContents = dict(map(lambda title, value: [title, value], columns, content))
        idColumn = columns[0]
        idContent = columnContents.get(idColumn)
        for title, value in columnContents.items():
            for keyword in keywords:
                if str(value).upper().find(keyword) != -1: LOGGER.error('{0} = {1}: Find keyword "{2}" in {3} = {4}'.format(idColumn, idContent, keyword, title, value))


def find_keywords(columns, allContents, keywords):
    for contents in allContents:
        find_keyword(columns=columns, contents=contents, keywords=keywords)


def main(directory, sheet, columns, keywords):
    check_path(path=directory)
    files = get_files(directory=directory)
    allContents = parse_excels(files=files, sheet=sheet, columns=columns)
    find_keywords(columns=columns, allContents=allContents, keywords=keywords)


if __name__ == '__main__':
    main(directory=OIB_DB_DIR, sheet='Measurement List', columns=['ID', 'Measurement Name', 'Description'], keywords=KEYWORDS)
    main(directory=OIB_DB_DIR, sheet='Counter List', columns=['ID', 'Counter Name', 'Description'], keywords=KEYWORDS)
    main(directory=OIB_NODB_DIR, sheet='Alarm List', columns=['ID', 'Alarm Name', 'Description'], keywords=KEYWORDS)
