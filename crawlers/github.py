# -*- coding: utf-8 -*-
"""
    github.py
    ~~~~~~~~~
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
    def handle(self, task, **kwargs):
        task = super(RequestHandler, self).handle(task)
        return task

class ParseHandler(BaseParseHandler):
    def get_profile():
        pass

    def get_followers():
        pass

    def handle(self, task):
        r = task['response']
        new_tasks = []
        item = None
        if task['type'] == 'get_profile':
            item = r.content
        elif task['type'] == 'get_followers':
            users= json.loads(r.content)
            for user in users:
                name = user['login']
                new_tasks.append({
                    'url': 'https://api.github.com/users/%s' % name,
                    'type': 'get_profile',
                        })
                new_tasks.append({
                        'url': 'https://api.github.com/users/%s/followers' % name,
                        'type': 'get_followers',
                        })
        return item, new_tasks

class Scheduler(BaseScheduler):
    def init_generator(self):
        task = {
                'url': 'https://api.github.com/users/atupal/followers',
                'type': 'get_followers',
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
