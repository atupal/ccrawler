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
from celeryapp.crawl_tasks import app
from celeryapp.celery import get_message_queue_size

from celery import group

tasks = app.tasks

for crawler in celeryconfig.crawlers:
    filepath = os.path.join(root_path, 'data/%s' % crawler.get('scheduler').filter_file_name)
    filepath = os.path.abspath(filepath)
    if not os.path.exists(filepath):
        tasks[crawler['name'] + '.schedule'].delay()
    #for dict_item in crawler['scheduler'].generator():
    #    group(tasks[crawler['name'] + '.request'].s(dict_item) 
    #            | tasks[crawler['name'] + '.parse'].s() 
    #           | tasks[crawler['name'] + '.pipeline'].s()).delay()

import time
cnt = 0
while 1:
    try:
        cnt += 1
        if (get_message_queue_size('parse') < config.max_task_queue_size * 5 and 
            get_message_queue_size('pipeline') < config.max_task_queue_size * 5 and
            get_message_queue_size('schedule') < config.max_task_queue_size * 15 and
            get_message_queue_size('request') < config.max_task_queue_size):
            for crawler in celeryconfig.crawlers:
                #tasks[crawler['name'] + '.schedule'].delay(check_task=True)
                for task in tasks[crawler['name']+'.schedule'].scheduler.new_tasks_generator():
                    if task.get('priority', None):
                        tasks[crawler['name']+'.request_priority'].delay(task)
                    else:
                        tasks[crawler['name']+'.request'].delay(task)

                if cnt >= 150:
                    if not config.multi_scheduler:
                        tasks[crawler['name']+'.schedule'].scheduler.save_filter()
                        cnt = 0
        time.sleep(2)
    except KeyboardInterrupt:
        exit(0)
