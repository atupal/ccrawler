# -*- coding: utf-8 -*-
"""
    example.py
    ~~~~~~~~~~
"""
import os
import sys
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_path, '..'))
sys.path.append(os.path.join(current_path, '../..'))

from request.baseRequestHandler import BaseRequestHandler
from parse.baseParseHandler import BaseParseHandler
from schedule.baseScheduler import BaseScheduler
from database.basePipeline import BasePipeline

import time
import datetime
import json
from bs4 import BeautifulSoup

class RequestHandler(BaseRequestHandler):
    def handle(self, task, use_proxy=False, **kwargs):
        task = super(RequestHandler, self).handle(task)
        return task

class ParseHandler(BaseParseHandler):
    def handle(self, task):
        r = task['response']
        soup = BeautifulSoup(r.text, "lxml")
        new_tasks = []
        if task['url_depth'] < 3:
            for link in soup.find_all('a'):
                item = {'url': link.get('href'), 'url_depth': task['url_depth']}
                new_tasks.append(item)
        return task, new_tasks

class Scheduler(BaseScheduler):
    def init_generator(self):
        task = {
                'url': 'http://qq.com'
                }
        yield task

class Pipeline(BasePipeline):
    def process(self, results):
        for r in results:
            self.print_result(r)

if __name__ == '__main__':
    from bin.stand_alone_run import BaseCrawler
    crawler = BaseCrawler(RequestHandler(), ParseHandler(), Scheduler(), Pipeline())
    crawler.run()
