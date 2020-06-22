# coding = utf-8

__author__ = 'Zhou Shengshuai'
__version__ = '1.0'

import logging
import os

import pandas
import pylab
from matplotlib import pyplot
from pylab import np
from snownlp import SnowNLP


class SentimentAnalyzer(object):
    def __init__(self):
        # 日志设置
        logging.basicConfig(format='%(asctime)s %(filename)s[line:%(lineno)d]%(levelname)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p', level=logging.INFO)
        # 设置字体，支持中文字体
        pyplot.rcParams['font.sans-serif'] = ['SimHei']
        # 字符显示，解决符号'-'显示为方块的问题
        pyplot.rcParams['axes.unicode_minus'] = False

    def read_csv_data(self, file, column):
        # 从CSV文件中读取B站'网评数据'
        data = pandas.read_csv(file, usecols=[column], encoding='utf-8')
        # 转换为网评数据集，并去掉NaN的行
        contents = data.dropna().values.tolist()
        return contents

    def analyze_sentiment_data(self, contents):
        # 定义字典变量，用来存放网评数据和情感分数（Key为网评数据，Value为情感分数）
        comment_scores = {}
        # 循环遍历网评数据集
        for content in contents:
            # 网评数据
            comment = content[0]
            try:
                # 判断网评数据是否为空，是否第一次情感分析。如果网评数据为空，则跳过；如果非第一次情感分析，则跳过，避免重复分析
                if comment and comment not in comment_scores:
                    # 网评数据对应的情感分数
                    score = SnowNLP(comment).sentiments
                    # 情感分数区间为[0, 1]，情感分数减0.5后的区间为[-0.5, 0.5]，这更能说明情感程序，即：负数说明负面情绪；0说明中性情绪；正数说明正面情绪
                    comment_scores[comment] = score - 0.5
                    logging.info('网评数据：{0} | 情感分数：{1}'.format(comment, score))
            except Exception as exception:
                logging.exception('Analyse comment sentiment with exception and then set default sentiment score with 0:\n{0}'.format(exception))
                logging.warning('网评数据：{0} | 默认情感分数：{1}'.format(comment, 0))
                # 网评情感分析异常时，赋值默认情感分数0，即：中性情绪
                comment_scores[comment] = 0
        return comment_scores

    def write_csv_data(self, file, comment_scores):
        # 字典变量的Key为网评数据集
        comments = comment_scores.keys()
        # 字典变量的Value为情感分数集
        scores = comment_scores.values()
        # 写入B站'网评数据'和'情感分数'到CSV文件中
        pandas.DataFrame(data=zip(comments, scores)).to_csv(file, header=False, index=False, mode='w', encoding='utf_8_sig')

    def draw_sentiment_data(self, comment_scores):
        # 字典变量的Key为网评数据集
        comments = comment_scores.keys()
        # 字典变量的Value为情感分数集
        scores = comment_scores.values()
        # 绘制网评情感统计分析图：X坐标为网评索引，Y坐标为情感分数，连线样式为虚线'--'，连线颜色为蓝色，坐标点形状为圆圈'o'，坐标点大小为5号，坐标点颜色为红色
        pylab.plot(np.arange(len(comments)), list(scores), linestyle='--', color='green', marker='o', markersize=4, markerfacecolor='red')
        # 统计分析图的标题
        pyplot.title(u'B站网评情感统计分析图')
        # 统计分析图的X坐标轴标签
        pyplot.xlabel(u'网评索引')
        # 统计分析图的Y坐标轴标签
        pyplot.ylabel(u'情感程度')
        # 统计分析图的Y坐标轴刻度：最小值为-0.5，最大值为0.5，步长为0.1
        pyplot.yticks(ticks=np.arange(start=-0.5, stop=0.5, step=0.1))
        # 显示统计分析图
        pyplot.show()

    def main(self):
        contents = self.read_csv_data(file=os.path.join('input', 'bsite_comments_data.csv'), column=8)
        comment_scores = self.analyze_sentiment_data(contents=contents)
        self.write_csv_data(file=os.path.join('output', 'bsite_sentiments_data.csv'), comment_scores=comment_scores)
        self.draw_sentiment_data(comment_scores=comment_scores)


if __name__ == '__main__':
    sentimentAnalyzer = SentimentAnalyzer()
    sentimentAnalyzer.main()
