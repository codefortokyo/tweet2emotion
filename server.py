#!/bin/env python
# -*- coding: utf-8 -*-

from datetime import date
import tornado.escape
from tornado import httpserver
from tornado import gen
from tornado.ioloop import IOLoop
import tornado.web
from tornado.options import define, options
import urllib2 as urllib

import os
import logging

### glocal variable
logger = None
define("port", default=8000, type=int)

import tweet2emotion
import text_analytics

def logger_setting():
    global logger

    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('server')
    return logger

class JapaneseHandler(tornado.web.RequestHandler):
    def get(self):
        lang  = self.get_argument('lang', "ja")
        tweet = self.get_argument('text', "")

        # URLdecode & UTf-8
        #tweet = urllib.unquote(tweet).encode('raw_unicode_escape').decode('utf-8')
        #tweet = u'バイリンガルニュースのマミさんが登場とな、楽しみだ。'
        tweet = tweet.encode('utf-8')


        length = len(tweet)
        if length > 0:
            ratio = tweet2emotion.get_emotion(tweet)
        else:
            ratio = 0.0

        logging.debug('emotion=%f:lang=%s:tweet=%s' % (ratio, lang, tweet))

        response = {
            #'tweet' : tweet,
            'emotion' : ratio,
            #'lang' : 'ja'
        }
        self.set_header('content-type', 'application/json; charset=UTF-8')
        self.write(response)

    #def post(self):
    #    self.write('POST - Hello, world')

class EnglishHandler(tornado.web.RequestHandler):
    def get(self):
        lang  = self.get_argument('lang', "en")
        tweet = self.get_argument('text', "")

        # URLdecode & UTf-8
        tweet = tweet.encode('utf-8')

        length = len(tweet)
        if length > 0:
            ratio = text_analytics.get_emotion(lang, tweet)
        else:
            ratio = 0.0

        logging.debug('emotion=%f:lang=%s:tweet=%s' % (ratio, lang, tweet))

        response = {
            #'tweet' : tweet,
            'emotion' : ratio,
            #'lang' : 'ja'
        }
        self.set_header('content-type', 'application/json; charset=UTF-8')
        self.write(response)

class SpanishHandler(tornado.web.RequestHandler):
    def get(self):
        lang  = self.get_argument('lang', "es")
        tweet = self.get_argument('text', "")

        # URLdecode & UTf-8
        tweet = tweet.encode('utf-8')

        length = len(tweet)
        if length > 0:
            ratio = text_analytics.get_emotion(lang, tweet)
        else:
            ratio = 0.0

        logging.debug('emotion=%f:lang=%s:tweet=%s' % (ratio, lang, tweet))

        response = {
            #'tweet' : tweet,
            'emotion' : ratio,
            #'lang' : 'ja'
        }
        self.set_header('content-type', 'application/json; charset=UTF-8')
        self.write(response)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/?", JapaneseHandler),
            (r"/ja/?", JapaneseHandler),
            (r"/en/?", EnglishHandler),
            (r"/es/?", SpanishHandler),
        ]
        tornado.web.Application.__init__(self, handlers)

def main():
    logger = logger_setting()

    # python server.py --port=8000
    tornado.options.parse_config_file(os.path.join(os.path.dirname(__file__), 'server.conf'))
    tornado.options.parse_command_line()

    logger.debug('run on port %d in %s mode' % (options.port, options.logging))

    tweet2emotion.initialize()

    app = Application()
    app.listen(options.port)
    IOLoop.instance().start()

if __name__ == '__main__':
    main()