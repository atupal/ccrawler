# -*- coding: utf-8 -*-
"""
    config.py
    ~~~~~~~~~

    Configuration fo crawlers: tasks, crawlers, etc.
"""

# crawler control
## pool/database
pool_size = 50
num_threads = 5
CRAWLER_TIMEOUT = 60 * 25 # 25 senconds
TASK_TIMEOUT = 5
QUEUE_SIZE = 500

## crawl control
error_retry_cnt = 3
pipeline_sleeptime = .1
new_task_check_time = .1
retry_time = 10 # seconds
max_retries = 3
rate_limit = '100/s'
max_task_queue_size = 1000

## task
task_batch_size = 100
new_task_check_interval = 7

# data store
broker = 'redis://127.0.0.1'
proxy_pool = {'host': '127.0.0.1', 'port': 6379}
tasks_pool = {'host': '127.0.0.1', 'port': 6379}
task_pool_key = 'jobtasks'
jd_mongo = {'host': '127.0.0.1', 'port': 27017}

# worker
GEVENT=1
CELERY=2
#worker_type = GEVENT
worker_type = CELERY
celery_task_retult_expires = 60 * 1

# log format
import logging
logging.basicConfig(format='%(levelname)s:\t%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
