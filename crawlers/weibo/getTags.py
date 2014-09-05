# -*- coding: utf-8 -*-

import os
import jieba
import json
import datetime
#from dateutil import parser
from collections import OrderedDict

current_path = os.path.dirname(os.path.abspath(__file__))

cat_file_name = 'catfile'
word_file_name = 'semanticTable_final'

cat_dict = {}
word_dict = {}

with open(os.path.join(current_path, cat_file_name), 'rb') as f:
    for line in f:
        infos = line.strip().split()
        cat_dict[infos[0]] = infos[1:]

with open(os.path.join(current_path, word_file_name), 'rb') as f:
    for line in f:
        try:
            infos = line.replace('\n', '').split('\t')
            word_dict[infos[0]] = {}
            for info in infos[1:]:
                info_d = info.split(':')
                word_dict[infos[0]][info_d[0]] = float(info_d[1])
        except:
            print line.replace('\n', '')

def getTags(text):
    words = jieba.cut(text)
    result_dict = {}
    for word in words:
        if len(word) <= 1:
            continue
        word = word.encode('utf-8')
        word_info = word_dict.get(word, None)
        if word_info:
            for wkey in word_info:
                result_dict[wkey.decode('utf-8')] = result_dict.get(
                    wkey, 0) + word_info[wkey]
                
    items = result_dict.items()
    items.sort(key=lambda x: x[1], reverse=1)
    ret = OrderedDict(items)
    return ret

import re
def parse_date(string):
    #datetime.datetime.strptime(re.sub(r"[+-]([0-9])+", "", "Tue May 08 15:14:45 +0800 2012"),"%a %b %d %H:%M:%S %Y")
    date = datetime.datetime.strptime(re.sub(r"[+-]([0-9])+", "", string),"%a %b %d %H:%M:%S %Y")
    return date

def getAc(statuses):
    if isinstance(statuses, basestring):
        statuses = json.loads(statuses)
    cnt = 0
    time_sum = datetime.timedelta(0)
    for now, pre in zip(statuses[:-1], statuses[1:]):
        #time_sum += parser.parse(now['time']) - parser.parse(pre['time'])
        # this way is fast more five times than above
        time_sum += parse_date(now['time']) - parse_date(pre['time']) 
        cnt += 1
        if cnt > 25:
            break

    if not cnt:
        return -1
    else:
        return (time_sum / cnt).total_seconds() / 86400.

def test():
    import requests
    resp = requests.get('http://127.0.0.1:5984/weibo/349ad6e24997064b6a3028b4de20e052').content
    import time
    st = time.time()
    for i in xrange(1000):
        content = json.loads(resp)
        print getAc(content['statuses'])
        string = ' '.join(map(lambda x: x.get('text'), content['statuses']))
        #ret = getTags(string)
        #print json.dumps(ret)
    print time.time() - st

if __name__ == '__main__':
   test()
