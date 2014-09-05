from __future__ import absolute_import

from gevent import monkey
import sys
if 'threading' in sys.modules:
   del sys.modules['threading']
monkey.patch_all()
from celery import Celery
from celery.signals import worker_shutdown

import config

app = Celery('ccrawler',
             #backend='redis://localhost',
             broker=config.broker,
             #broker='redis://localhost:8888',
             include=['celeryapp.common_tasks', 'celeryapp.crawl_tasks']
       )

app.conf.update(
        CELERY_TASK_RESULT_EXPIRES=config.celery_task_retult_expires,
        )
app.config_from_object('celeryconfig')

import celeryconfig
@worker_shutdown.connect
def save_state(sender=None, conf=None, **kwargs):
    if not config.multi_scheduler:
        for crawler in celeryconfig.crawlers:
            app.tasks[crawler['name'] + '.schedule'].scheduler.save_filter()

import redis
import re
IP = re.compile(r'\d{1,3}(?:\.\d{1,3}){3}(?::\d{1,6})?')
def get_message_queue_size(queue_name):
    client = redis.Redis(IP.findall(config.broker)[0])
    length = client.llen(queue_name)
    return length

if __name__ == '__main__':
    app.start()
