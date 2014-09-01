#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
    baseRequestHandler.py
    ~~~~~~~~~~~~~~~~~~~~~

    Base request handler
"""
import gevent
from gevent import monkey
monkey.patch_all()
import requests
import logging
import socket
import time

from requests import ConnectionError
from random import choice

from .response import Response
import proxy
import cookie

class BaseRequestHandler(object):

    def __init__(self, use_proxy=False, proxy_module=proxy, cookie_module=cookie):
        self.use_proxy = use_proxy
        self.proxy_module = proxy
        self.cookie_module = cookie_module
        self._proxy_pool = []
        self._proxy_pool_size = 0
        self._redis_proxy_pool_connetion = None
        self._proxy_lock = gevent.lock.Semaphore()
        self._cookie_pool = {}

    def handle(self, task, **kwargs):
        return self.request(task, **kwargs)

    def request(self, task, **kwargs):
        url = task.get('url')
        if not url:
            logging.error('invalid url: emptry url!')
            return task

        _kwargs = {
                'params': {},  # dict or bytes
                'data': {},  # dict, bytes or file object
                'headers': {'user-agent': 'googleBot'},
                'cookies': {},  # dict or cookiejar object
                'files': {},
                'auth': None,
                'timeout': 5,
                'allow_redirects': True,
                'proxies': {},
                'verify': False,
                'stream': False,
                'cert': None,
                }
        _kwargs.update(kwargs)
        if self.use_proxy or task.get('proxy'):
            proxy = task.get('proxy') or self._pop_proxy()
            _kwargs['proxies'].update(proxy)
        if (not task.get('method')
            or task.get('method', '').uppper() == 'GET'):
            method = 'get'
        elif task.get('method', '').upper() == 'POST':
            method = 'post'
        else:
            raise 'Invalid or unsupported method!'

        proxy_retry_cnt = 0
        while 1:
            try:
                resp = requests.request(method, url, **_kwargs)
                break
            except (requests.exceptions.ProxyError,
                    requests.exceptions.Timeout, 
                    ConnectionError,
                    socket.timeout) as e:
                proxy_retry_cnt += 1
                if self.use_proxy:
                    proxy = self._pop_proxy()
                    _kwargs['proxies'].update(proxy)
                if proxy_retry_cnt >= 10:
                    raise e
        if self.use_proxy and proxy:
            self._add_proxy(proxy)

        task['response'] = resp.content
        if resp.status_code != 200:
            #logging.error('not 200 http response')
            #logging.error(url)
            #logging.error(_kwargs)
            raise Exception('not 200 http response')

        if 'url_depth' in task:
            task['url_depth'] += 1
        else:
            task['url_depth'] = 1
        return task

    def _pop_proxy(self):
        fetch_cnt = 0
        with self._proxy_lock:
            while self._proxy_pool_size <= 0:
                try:
                    self._fetch_new_proxy_list()
                except:
                    raise
                fetch_cnt += 1
                if fetch_cnt == 3:
                    raise Exception('Can not fetch proxy list!')

        proxy = self._proxy_pool.pop(0)
        self._proxy_pool_size -= 1
        return proxy
    
    def _get_fastest_proxy(self):
        pass
    
    def _add_proxy(self, proxy):
        self._proxy_pool.append(proxy)
        self._proxy_pool_size += 1

    def _fetch_new_proxy_list(self):
        proxy_list = self.proxy_module.get_proxy_list()
        #while self._proxy_checking:
            #gevent.sleep(0.1)
        self._proxy_pool += proxy_list
        self._proxy_pool_size += len(proxy_list)

    def _check_proxy_pool_health(self):
        self._proxy_checking = True
        jobs = []
        self._proxy_checking = False

    @property
    def proxy_pool_size(self):
        return self._proxy_pool_size

def test():
    requestHandler = BaseRequestHandler()
    jobs = []
    st = time.time()
    for i in xrange(100):
        jobs.append( gevent.spawn( requestHandler.handle, {'url': 'http://baidu.com'} ) )
    for job in jobs:
        print job.get()
    gevent.joinall(jobs)
    print time.time() - st

if __name__ == '__main__':
    test()
