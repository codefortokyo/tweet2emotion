# coding:UTF-8

from requests_oauthlib import OAuth1Session
from requests.exceptions import ConnectionError, ReadTimeout, SSLError
import json, time, exceptions, sys, datetime, pytz, re, unicodedata, pymongo
import oauth2 as oauth
import urllib2 as urllib
import MeCab as mc
from collections import defaultdict
from pymongo import MongoClient
from httplib import IncompleteRead
import numpy as np

'''
Twitter Stream APIデータに対して初歩的な感情分析を試みる。
http://qiita.com/kenmatsu4/items/52ab6deffdd61e7d8c0f
CaboChaで始める係り受け解析
http://qiita.com/nezuq/items/f481f07fc0576b38e81d

'''

import logging
from logging import FileHandler, Formatter
import logging.config

connect = MongoClient('localhost', 27017)
db = connect.word_info
posi_nega_dict = db.posi_nega_dict
db2 = connect.twitter
streamdata = db2.streamdata

def dict_make():
    # 単語のポジ・ネガ辞書のmongoDBへのインポート

    # 日本語評価極性辞書（用言編）ver.1.0（2008年12月版）をmongodbへインポート
    # ポジの用語は 1 ,ネガの用語は -1 と数値化する
    with open("wago.121808.pn", 'r') as f:
        for l in f.readlines():
            l = l.split('\t')
            l[1] = l[1].replace(" ", "").replace('\n', '')
            value = 1 if l[0].split('（')[0] == "ポジ" else -1
            posi_nega_dict.insert({"word": l[1].decode('utf-8'), "value": value})

    # 日本語評価極性辞書（名詞編）ver.1.0（2008年12月版）をmongodbへインポート
    # pの用語は 1 eの用語は 0 ,nの用語は -1 と数値化する
    with open("pn.csv.m3.120408.trim", 'r') as f:
        for l in f.readlines():
            l = l.split('\t')

            if l[1] == "p":
                value = 1
            elif l[1] == "e":
                value = 0
            elif l[1] == "n":
                value = -1

            posi_nega_dict.insert({"word": l[0].decode('utf-8'), "value": value})

def initialize():
    print 'initialize!!'

if __name__ == '__main__':
    initialize()
    dict_make()
