#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import sys
current_path = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.join(current_path, '..'))
sys.path.append(root_path)
# chagne work dir
os.chdir(root_path)
import config
import celeryconfig
import logging
from celeryapp.crawl_tasks import app
from celeryapp.celery import get_message_queue_size

from celery import group

tasks = app.tasks

for crawler in celeryconfig.crawlers:
    filepath = os.path.join(root_path, 'data/%s' % crawler.get('scheduler').filter_file_name)
    filepath = os.path.abspath(filepath)
    if not os.path.exists(filepath):
        #tasks[crawler['name'] + '.schedule'].delay()
        for task in tasks[crawler['name']+'.schedule'].scheduler.init_generator():
            if task.get('priority', None):
                #app.tasks[self.crawler_name+'.request_priority'].delay(task)
                tasks[crawler['name']+'.request_priority'].apply_async((task, ), compression='zlib')
            else:
                #tasks[crawler['name']+'.request'].delay(task)
                tasks[crawler['name']+'.request'].apply_async((task, ), compression='zlib')


    #for dict_item in crawler['scheduler'].generator():
    #    group(tasks[crawler['name'] + '.request'].s(dict_item) 
    #            | tasks[crawler['name'] + '.parse'].s() 
    #           | tasks[crawler['name'] + '.pipeline'].s()).delay()

from gevent import monkey
from gevent.pool import Pool
from gevent.lock import Semaphore
import gevent
import json
monkey.patch_all()

scheduel_lock = Semaphore()

import time
filtered_newtasks = []

def schedule():
    global filtered_newtasks
    while 1:
        try:
            if (get_message_queue_size('parse') < config.max_task_queue_size * 2 and 
                get_message_queue_size('pipeline') < config.max_task_queue_size * 2 and
                get_message_queue_size('schedule') < config.max_task_queue_size * 2 and
                get_message_queue_size('request') < config.max_task_queue_size):
                for crawler in celeryconfig.crawlers:
                    #tasks[crawler['name'] + '.schedule'].delay(check_task=True)
                    #for task in tasks[crawler['name']+'.schedule'].scheduler.new_tasks_generator():
                    #    if task.get('priority', None):
                    #        #tasks[crawler['name']+'.request_priority'].delay(task)
                    #        tasks[crawler['name']+'.request_priority'].apply_async((task, ), compression='zlib')
                    #    else:
                    #        #tasks[crawler['name']+'.request'].delay(task)
                    #        tasks[crawler['name']+'.request'].apply_async((task, ), compression='zlib')
                    with scheduel_lock:
                        db = tasks[crawler['name']+'.schedule'].scheduler.get_redis_connection()
                        new_tasks = db.lpop(config.filtered_task_pool_key)
                        if new_tasks:
                            new_tasks = json.loads(new_tasks)
                        else:
                            new_tasks = filtered_newtasks
                            filtered_newtasks = []

                        for task in new_tasks:
                            if task.get('priority', None):
                                #tasks[crawler['name']+'.request_priority'].delay(task)
                                tasks[crawler['name']+'.request_priority'].apply_async((task, ), compression='zlib')
                            else:
                                #tasks[crawler['name']+'.request'].delay(task)
                                tasks[crawler['name']+'.request'].apply_async((task, ), compression='zlib')
            else:
                gevent.sleep(1)
        except Exception as exc:
            logging.exception(exc)
            for crawler in celeryconfig.crawlers:
                tasks[crawler['name']+'.schedule'].scheduler.save_filter()
            raise

def filter_task():
    global filtered_newtasks
    while 1:
        for crawler in celeryconfig.crawlers:
            #tasks[crawler['name'] + '.schedule'].delay(check_task=True)
            for task in tasks[crawler['name']+'.schedule'].scheduler.new_tasks_generator():
                with scheduel_lock:
                    if len(filtered_newtasks) >= config.task_batch_size:
                        db = tasks[crawler['name']+'.schedule'].scheduler.get_redis_connection()
                        db.lpush(config.filtered_task_pool_key, json.dumps(filtered_newtasks))
                        filtered_newtasks = [task]
                    else:
                        filtered_newtasks.append(task)

try:
    p = Pool(20)
    for i in xrange(5):
        p.spawn(schedule)
        p.spawn(filter_task)
    p.join()
except:
    for crawler in celeryconfig.crawlers:
        tasks[crawler['name']+'.schedule'].scheduler.save_filter()
