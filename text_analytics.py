#!/bin/env python
# -*- coding: utf-8 -*-

import httplib, urllib, base64
import json

import logging
from logging import FileHandler, Formatter
import logging.config

def logger_setting():
    #import logging
    #from logging import FileHandler, Formatter
    #import logging.config

    global logger

    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('filelogger')
    return logger

def get_emotion(lang, tweet):

    # logginig setup
    logger_setting()

    # https://westus.dev.cognitive.microsoft.com/docs/services/TextAnalytics.V2.0/operations/56f30ceeeda5650db055a3c9
    # https://www.microsoft.com/cognitive-services/en-us/text-analytics/documentation
    # https://github.com/Microsoft/CognitiveServices-Documentation
    headers = {
    # Request headers
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': 'acecc870695f4028a2404bf4fa28f279',
    }

    params = urllib.urlencode({
    })

    body = {
        "documents": [
            {
            "language": lang,
            "id": "1",
            "text": tweet
            }
        ]
    }

    score = 0.0

    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/text/analytics/v2.0/sentiment?%s" % params, str(body), headers)
        response = conn.getresponse()
        text = response.read()
        logger.debug(text)

        data   = json.loads(text)
        doc    = data["documents"]
        err    = data["errors"]

        length = len(err)
        if length > 0:
            return score

        length = len(doc)
        if length > 0:
            d0     = doc[0]
            score  = d0["score"]

    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
    finally:
        conn.close()

    return score