# -*- coding: utf-8 -*-
"""
    config.py
    ~~~~~~~~~

    Configuration fo crawlers: tasks, crawlers, etc.
"""

# crawler control
## pool/database
pool_size = 1000
num_threads = 5
CRAWLER_TIMEOUT = 60 * 25 # 25 senconds
TASK_TIMEOUT = 5
QUEUE_SIZE = 50

## crawl control
error_retry_cnt = 3
pipeline_sleeptime = .1
new_task_check_time = .1
retry_time = 10 # seconds
max_retries = 3
rate_limit = '1000/s'
time_limit = 100
import os
if 'atupal' in os.environ['HOME']:
    max_task_queue_size = 1000
else:
    max_task_queue_size = 100000

## task
import os
if 'atupal' in os.environ['HOME']:
    task_batch_size = 100
else:
    task_batch_size = 1000
new_task_check_interval = 7

# data store
import os
if 'atupal' in os.environ['HOME']:
    broker = 'redis://127.0.0.1'
    proxy_pool = {'host': '127.0.0.1', 'port': 6379}
    tasks_pool = {'host': '127.0.0.1', 'port': 8888}
    rfilter_redis = '127.0.0.1'
    task_pool_key = 'newtasks'
    filtered_task_pool_key = 'filtered_newtasks'
    jd_mongo = {'host': '127.0.0.1', 'port': 27017}
    couchdb = 'http://127.0.0.1:5984/'
else:
    broker = 'redis://192.168.0.10'
    proxy_pool = {'host': '192.168.0.10', 'port': 6379}
    tasks_pool = {'host': '192.168.0.10', 'port': 8888}
    rfilter_redis = '192.168.0.10'
    task_pool_key = 'newtasks'
    filtered_task_pool_key = 'filtered_newtasks'
    jd_mongo = {'host': '192.168.0.10', 'port': 27017}
    couchdb = 'http://192.168.0.10:5984/'

# worker
GEVENT=1
CELERY=2
#worker_type = GEVENT
worker_type = CELERY
celery_task_retult_expires = 60 * 1

# cluster
multi_scheduler = False

# schedule
save_filter_interval = 200000

# log format
import logging
logging.basicConfig(format='%(levelname)s:\t%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
