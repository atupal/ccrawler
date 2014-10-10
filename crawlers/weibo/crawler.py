# -*- coding: utf-8 -*-
"""
    crawl.py
    ~~~~~~~~

    crawl all weibo users's profile, tags, and first 100 statuses.
    Only profile, tags, itags and ac(analyzed from first 100 statuses)
    will be saved.
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
import urlparse
from bs4 import BeautifulSoup

sina_crawler_global_api = 'http://103.29.133.173/APIPOOL/?method=sina_crawler.global_api&api={0}'
sina_crawler_search_api = 'http://103.29.133.173/APIPOOL?method=sina_crawler.search_api&{0}'
sina_crawler_gsid_api = 'http://103.29.133.173/APIPOOL?method=sina_crawler.gsid_api&api={0}'

#get_friends_url = 'friendships/friends&cursor=%(cursor)d&uid=%(uid)s'
get_friends_url = 'friendships/friends/ids&uid=%(uid)s&count=5000'
get_profile_url = '2/users/show&uid=%(uid)s&has_profile=1'
get_timeline_url = 'statuses/user_timeline&uid=%(uid)s&feature=1&count=100'
get_tag_url = 'tags&uid=%(uid)s'

class RequestHandler(BaseRequestHandler):

    def handle(self, task, use_proxy=False, **kwargs):
        retry_cnt = 0
        while retry_cnt < 15:
            task = super(RequestHandler, self).handle(task)
            resp = task['response']
            data = json.loads(resp['content'])
            if (data['return_code'] == 0 and not 'error' in data['data'] 
                   and not 'errno' in data['data'] and not 'errmsg' in data['data']):
                return task
            retry_cnt += 1
        raise Exception('Api error!')

def get_tasks(uid):
    new_tasks = []
    new_tasks.append({
        'url': sina_crawler_global_api.format(get_friends_url % { 'uid': str(uid) }),
        'type': 'get_friends',
        })
    new_tasks.append({
        'url': sina_crawler_gsid_api.format(get_profile_url % { 'uid': str(uid) }),
        'type': 'get_profile',
        })
    new_tasks.append({
        'url': sina_crawler_global_api.format(get_timeline_url % { 'uid': str(uid) }),
        'type': 'get_timeline',
        })
    new_tasks.append({
        'url': sina_crawler_global_api.format(get_tag_url % { 'uid': str(uid) }),
        'type': 'get_tag',
        })
    return new_tasks

class ParseHandler(BaseParseHandler):

    def get_uid_from_url(self, url):
        parse = urlparse.urlparse(url)
        qs = urlparse.parse_qs(parse.query)
        uid = None
        for uid in qs['uid']:pass
        return uid

    def get_friends(self, task):
        resp = task['response']
        friends = json.loads(resp['content'])
        ret = {}
        new_tasks = []
        ret['friends'] = friends['data']['ids']
        ret['uid'] = self.get_uid_from_url(task['url'])

        for uid in friends['data']['ids']:
            new_tasks.extend(get_tasks(uid))

        return ret, new_tasks

    def get_profile(self, task):
        resp = task['response']
        data = json.loads(resp['content'])['data']
        data['uid'] = data['idstr']
        delkeys = ['cover_image_phone_level', 'domain', 'avatar_large',
                'idstr', 'id', 'profile_image_url', 'online_status', 'avatar_hd', 'following', 'cover_image', 'cover_image_phone']
        for key in delkeys:
            if key in data: del data[key]
        return data, []

    def get_timeline(self, task):
        from getTags import getTags, getAc
        resp = task['response']
        data = json.loads(resp['content'])['data']
        ret = {}
        statuses = []
        for status in data['statuses']:
            statuses.append({
                'time': status['created_at'],
                'source': BeautifulSoup(status['source']).getText(),
                'text': status['text'],
                })
        #ret['statuses'] = statuses
        ret['uid'] = self.get_uid_from_url(task['url'])
        string = ' '.join(map(lambda x: x.get('text'), statuses))
        ret['itags'] = getTags(string)
        ret['ac'] = getAc(statuses)
        return ret, []

    def get_tag(self, task):
        ret = {}
        resp = task['response']
        data = json.loads(resp['content'])['data']
        ret['tags'] = data
        ret['uid'] = self.get_uid_from_url(task['url'])
        return ret, []

    def handle(self, task):
        h = { 
              'get_friends': self.get_friends,
              'get_profile': self.get_profile,
              'get_timeline': self.get_timeline,
              'get_tag': self.get_tag, 
            }
        return h[task['type']](task)

class Scheduler(BaseScheduler):
    def init_generator(self):
        for task in get_tasks('1232785811'):
            yield task

class Pipeline(BasePipeline):
    def process(self, results):
        for r in results:
            #self.print_result(r)
            self.save_to_couchdb(r)

if __name__ == '__main__':
    from bin.stand_alone_run import BaseCrawler
    crawler = BaseCrawler(RequestHandler(), ParseHandler(), Scheduler(), Pipeline())
    crawler.run()
