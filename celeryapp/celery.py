from __future__ import absolute_import

from gevent import monkey
import sys
if 'threading' in sys.modules:
   del sys.modules['threading']
monkey.patch_all()
from celery import Celery

import config

app = Celery('ccrawler',
             #backend='redis://localhost',
             broker='redis://localhost:6379',
             #broker='redis://localhost:8888',
             include=['celeryapp.common_tasks', 'celeryapp.crawl_tasks']
       )

app.conf.update(
        CELERY_TASK_RESULT_EXPIRES=config.celery_task_retult_expires,
        )
app.config_from_object('celeryconfig')

class Add(app.Task):

    def run(self, x, y):
        return x+y
    
app.tasks.register(Add)

import redis
def get_message_queue_size(queue_name):
    client = redis.Redis()
    length = client.llen(queue_name)
    return length

if __name__ == '__main__':
    app.start()
