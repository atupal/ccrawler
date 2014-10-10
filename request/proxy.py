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
reload(sys)
sys.setdefaultencoding('utf-8')
import time
if 'threading' in sys.modules:
    del sys.modules['threading']
import gevent
import gevent.monkey
from gevent.pool import Pool
gevent.monkey.patch_all()

IP = re.compile(r'\d{1,3}(?:\.\d{1,3}){3}(?::\d{1,6})?')

def get_real_ip(proxy):
    #url = 'http://www.ip.cn/'
    #resp = requests.get(url, proxies=proxy, timeout=7, headers={'user-agent': 'curl/7.37.0',})
    url = 'http://www.baidu.com/s?wd=ip'
    #url = 'http://20140507.ip138.com/ic.asp'
    resp = requests.get(url, proxies=proxy, timeout=7, headers={'user-agent': 'chrome',})
    #print resp
    if resp.status_code != 200:
      raise Exception
    real_ip =  IP.findall(resp.content[resp.content.find('我的ip地址'):])[0]
    #real_ip =  IP.findall(resp.content)[0]
    if proxy:
        #print real_ip, proxy['http']
        pass
    return real_ip

local_ip = get_real_ip({})

def check(proxy):
    try:
        st = time.time()
        real_ip = get_real_ip(proxy)
        if not real_ip in  proxy['http']:
          if real_ip  == local_ip:
            raise Exception
        if real_ip:
            #print r, proxy, "\t%dms" % int((time.time() - st)*1000)
            proxy['speed'] = int((time.time() - st)*1000)
            #print proxy['http']
            return proxy
    except (requests.exceptions.Timeout, socket.timeout,requests.exceptions.ProxyError):
        #print 'timeout'
        return None
    except Exception as e:
        #print str(e)
        #print 'Can not connect'
        return None

def get_proxy_list_from_gevent(tasks):
    proxy_list = []
    jobs = []
    p = Pool(1000)
    for task in tasks:
        jobs.append(p.spawn(check, task))

    for job in jobs:
        proxy = job.get()
        if proxy:
            proxy_list.append(proxy)
    return proxy_list

def get_proxy_list_pachong():
    url = 'http://pachong.org/anonymous.html'
    res = requests.get(url, timeout=7)
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

    ret = table
    jobs = []
    for row in ret[1:51]:
        if '空闲' in row[5].encode('utf-8'):
            proxy = {'http': 'http://%s:%s' % (row[1], row[2])}
            proxy['https'] = proxy['http']
            jobs.append(proxy)
    return jobs

def get_proxy_list_cnproxy():
    #soup('table')[0]('tr')[2]('td')
    url = 'http://cn-proxy.com/'
    resp = requests.get(url, timeout=7)
    soup = BeautifulSoup(resp.content)
    jobs = []
    for table in soup('table'):
      for tr in table('tr'):
        tds = tr('td')
        if len(tds) >= 2:
          proxy = {
              'http': 'http://%s:%s' % (tds[0].getText(), tds[1].getText()),
              'https': 'http://%s:%s' % (tds[0].getText(), tds[1].getText()),
              }
          jobs.append(proxy)

    return jobs

def get_proxy_list_ipcn():
    url = 'http://proxy.ipcn.org/proxylist.html'
    resp = requests.get(url, headers={'user-agent': 'chrome'}, timeout=7)
    jobs = []
    for ip in IP.findall(resp.content):
        proxy = {
              'http': 'http://%s' % ip,
              'https': 'http://%s' % ip,
              }
        jobs.append(proxy)
    return jobs

def get_proxy_list_proxy_ru_gaoni():
    url = 'http://proxy.com.ru/gaoni/list_%d.html'
    jobs = []
    for i in xrange(1, 7):
        try:
            resp = requests.get(url%i, timeout=7)
        except:
            continue
        if resp.status_code != 200:
            continue
        soup = BeautifulSoup(resp.content)
        for table in soup('table'):
          for tr in table('tr'):
            tds = tr('td')
            if len(tds) >= 3:
              proxy = {
                  'http': 'http://%s:%s' % (tds[1].getText(), tds[2].getText()),
                  'https': 'http://%s:%s' % (tds[1].getText(), tds[2].getText()),
                  }
              jobs.append(proxy)
    return jobs

def get_proxy_list_proxy_ru_niming():
    url = 'http://proxy.com.ru/niming/list_%d.html'
    jobs = []
    for i in xrange(1, 7):
        try:
            resp = requests.get(url%i, timeout=7)
        except:
            continue
        if resp.status_code != 200:
            continue
        soup = BeautifulSoup(resp.content)
        for table in soup('table'):
          for tr in table('tr'):
            tds = tr('td')
            if len(tds) >= 3:
              proxy = {
                  'http': 'http://%s:%s' % (tds[1].getText(), tds[2].getText()),
                  'https': 'http://%s:%s' % (tds[1].getText(), tds[2].getText()),
                  }
              jobs.append(proxy)
    return jobs

def get_proxy_list_itmop():
    ip_list = []
    jobs = []
    for url in xrange(1690, 10000):
        try:
            url = 'http://www.itmop.com/proxy/post/%s.html' % url
            # url = 'http://www.cz88.net/proxy/index_%s.aspx' % url
            result = requests.get(url, timeout=10).text
            pattern = re.compile(r'(\d+\.\d+\.\d+\.\d+)[: ](\d+)')
            ilist = pattern.findall(result)
            for ip in ilist:
                proxy = {
                        'http': 'http://%s:%s' % (ip[0], ip[1]),
                        'https': 'http://%s:%s' % (ip[0], ip[1]),
                        }
                jobs.append(proxy)
        except:
            raise
            break

    return jobs

def get_proxy_list():
    print 'fetching proxy list from free proxy list site...'
    ret = []
    jobs = []
    proxy_source_methos = [
            get_proxy_list_pachong,
            get_proxy_list_cnproxy,
            get_proxy_list_ipcn,
            get_proxy_list_proxy_ru_gaoni,
            get_proxy_list_proxy_ru_niming,
            #get_proxy_list_itmop,
            ]
    for f in proxy_source_methos:
        try:
            jobs.append(gevent.spawn(f))
        except requests.exceptions.Timeout:
            pass
        except:
            pass
    #ret.extend(get_proxy_list_pachong())
    #ret.extend(get_proxy_list_cnproxy())
    for job in jobs:
        ret.extend(job.get())
    ret = get_proxy_list_from_gevent(ret)
    print 'proxy list fetch finished.'
    return ret

def test():
    st = time.time()
    proxy_list = get_proxy_list()
    print time.time() - st
    #print proxy_list
    print len(proxy_list)

if __name__ == '__main__':
    test()
