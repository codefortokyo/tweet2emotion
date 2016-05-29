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

import sys

### glocal variable
logger = None
posi_nega_dict = None

'''
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

'''


def str_to_date_jp(str_date):
    dts = datetime.datetime.strptime(str_date,'%a %b %d %H:%M:%S +0000 %Y')
    return pytz.utc.localize(dts).astimezone(pytz.timezone('Asia/Tokyo'))

def mecab_analysis(sentence):
    #t = mc.Tagger('-Ochasen -d /usr/local/Cellar/mecab/0.996/lib/mecab/dic/mecab-ipadic-neologd/')
    t = mc.Tagger('-Ochasen')
    sentence = sentence.replace('\n', ' ')
    #text = sentence.encode('utf-8')
    text = sentence
    node = t.parseToNode(text)
    result_dict = defaultdict(list)
    for i in range(140):  # ツイートなのでMAX140文字
        if node.surface != "":  # ヘッダとフッタを除外
            word_type = node.feature.split(",")[0]
            if word_type in ["形容詞", "動詞","名詞", "副詞"]:
                plain_word = node.feature.split(",")[6]
                if plain_word !="*":
                    result_dict[word_type.decode('utf-8')].append(plain_word.decode('utf-8'))
        node = node.next
        if node is None:
            break
    return result_dict


def isexist_and_get_data(data, key):
    return data[key] if key in data else None

# -1 〜 1の範囲で与えられた文章（単語リスト）に対する感情値を返す。(1: 最もポジ、-1:最もネガ)
def get_setntiment(word_list):
    global posi_nega_dict

    # 感情度の設定(検索高速化のためハッシュ検索ができるよう辞書オブジェクトに入れ込む)
    pn_dict = {data['word']: data['value'] for data in posi_nega_dict.find({}, {'word': 1, 'value': 1})}

    val = 0
    score = 0
    word_count = 0
    val_list = []
    for word in word_list:
        val = isexist_and_get_data(pn_dict, word)
        val_list.append(val)
        if val is not None and val != 0: # 見つかればスコアを足し合わせて単語カウントする
            score += val
            word_count += 1

    logger.debug(','.join(word_list).encode('utf-8'))
    logger.debug(val_list)
    return score/float(word_count) if word_count != 0. else 0.

def get_emotion(tweet):
    try:
        result = mecab_analysis(tweet)

        # 感情分析結果を追加 ####################
        word_list = [word for k in result.keys() for word in result[k] ]
        ratio = get_setntiment(word_list)
        return ratio

    except IncompleteRead as e:
        logger.error( '=== エラー内容 ===')
        logger.error(  'type:' + str(type(e)))
        logger.error(  'args:' + str(e.args))
        logger.error(  'message:' + str(e.message))
        logger.error(  'e self:' + str(e))
        try:
            if type(e) == exceptions.KeyError:
                logger.error( data.keys())
        except:
            pass

    except Exception as e:
        logger.error( '=== エラー内容 ===')
        logger.error( 'type:' + str(type(e)))
        logger.error( 'args:' + str(e.args))
        logger.error( 'message:' + str(e.message))
        logger.error( 'e self:' + str(e))
        try:
            if type(e) == exceptions.KeyError:
                logger.error( data.keys())
        except:
            pass
    except:
        logger.error( "error.")

def logger_setting():
    #import logging
    #from logging import FileHandler, Formatter
    #import logging.config

    global logger

    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('filelogger')
    return logger

def db_setting():
    global posi_nega_dict

    # database setup
    connect = MongoClient('localhost', 27017)
    db = connect.word_info
    posi_nega_dict = db.posi_nega_dict

def initialize():
    #print 'initialize'

    # logginig setup
    logger_setting()

    # database setup
    db_setting()

if __name__ == '__main__':

    ## get form params ##
    params = sys.argv
    length = len(params)

    if (length != 2):
        print 'Usage: python %s parameter' % params[0]
        quit()


    value = params[1]

    initialize()
    logger.info("start.")

    #value = u'バイリンガルニュースのマミさんが登場とな、楽しみだ。'
    ratio = get_emotion(value)

    logger.debug("ratio = %f" % (ratio))
    logger.info("finished.")
