#!/usr/bin/env pythno2
# -*- coding: utf-8 -*-
"""
    baseParseHandler.py
    ~~~~~~~~~~~~~~~~~~~
"""
import redis
import lxml.html

import config

class BaseParseHandler(object):
    def __init__(self):
        self.redis_connection_pool = redis.ConnectionPool(
                host=config.tasks_pool.get('host') or '127.0.0.1',
                port=config.tasks_pool.get('port') or 6379,
                db=config.tasks_pool.get('db') or 0
            )
        # this crawler_name will set when regist  celelry task: tasks.py
        self.crawler_name = 'unset'

    def get_redis_connection(self):
        return redis.Redis(connection_pool=self.redis_connection_pool)

    def handle(self, task):
        return task.get('response'), []

    def extract_by_xpath(self, xpath, content):
        try:
            x = lxml.html.fromstring(content)
            return x.xpath(xpath)
        except:
            return []

    def parse_href(self):
        pass

    def parse_img(self):
        pass

def test():
    parseHandler = BaseParseHandler()
    import requests
    r = requests.get('https://github.com/atupal')
    print parseHandler.extract_by_xpath('//*[@id="site-container"]/div/div/div[1]/ul/li[1]/text()', r.text)

if __name__ == '__main__':
    test()
