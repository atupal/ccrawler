# -*- coding: utf-8 -*-
"""
   proxy.py
   ~~~~~~~~

   get proxy list from http://pachong.com
"""

from bs4 import BeautifulSoup
import requests
import re
import socket
import sys
import time
if 'threading' in sys.modules:
    del sys.modules['threading']
import gevent
import gevent.monkey
gevent.monkey.patch_all()

def get_raw_proxy_list():
    url = 'http://pachong.org/anonymous.html'
    res = requests.get(url)
    text = res.content
    soup = BeautifulSoup(text)
    table = [
                [cell.text for cell in row('td')]  for row in soup('tr')
            ]

    for js in soup('script'):
        if 'var' in js.text:
            exec ( js.getText().replace('var', '').strip() )
    pattern = re.compile(r'write\((.*)\)')
    for t in table[1:51]:
        t[2] = re.findall(pattern, t[2])[0]
        exec('port=%s' % t[2])
        t[2] = str(port)

    return table

def check(proxy):
    try:
        st = time.time()
        r = requests.get('http://baidu.com', proxies=proxy, timeout=3)
        if r.status_code == 200 and 'meta http-equiv="refresh" content="0;url=http://www.baidu.com/"' in r.content:
            #print r, proxy, "\t%dms" % int((time.time() - st)*1000)
            proxy['speed'] = int((time.time() - st)*1000)
            return proxy
        else:
            #print '403 or 404'
            return None
    except (requests.exceptions.Timeout, socket.timeout,requests.exceptions.ProxyError):
        #print 'timeout'
        return None
    except Exception as e:
        print str(e)
        #print 'Can not connect'
        return None

def get_proxy_list():
    ret = get_raw_proxy_list()
    jobs = []
    proxy_list = []
    for row in ret[1:51]:
        if '空闲' in row[5].encode('utf-8'):
            proxy = {'http': 'http://%s:%s' % (row[1], row[2])}
            proxy['https'] = proxy['http']
            jobs.append( gevent.spawn(check, proxy) )
    #gevent.joinall(jobs)
    for job in jobs:
        proxy = job.get()
        if proxy:
            proxy_list.append(proxy)
    return proxy_list

def test():
    print get_proxy_list()

if __name__ == '__main__':
    test()
