# -*- coding: utf-8 -*-
'''
    baseScheduler.py
    ~~~~~~~~~~~~~~~~
'''
import os
import sys
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(root)

import config
import redis
import gevent
import json
from redisfilter import ScalableRedisBloomFilter

class BaseScheduler(object):
    def __init__(self, ):
        self.redis_connection_pool = redis.ConnectionPool(
                host=config.tasks_pool.get('host') or '127.0.0.1',
                port=config.tasks_pool.get('port') or 6379,
                db=config.tasks_pool.get('db') or 0
                )
        self.task_batch = []
        self.rfilter = ScalableRedisBloomFilter(
                initial_capacity=10000, error_rate=0.0001,
                prefixbitkey='ccrawler', clear_filter=True)

    def get_redis_connection(self):
        return redis.Redis(connection_pool=self.redis_connection_pool)

    def init_tasks_generator(self):
        raise NotImplementedError

    def new_tasks_generator(self):
        db = self.get_redis_connection()
        if config.worker_type == config.GEVENT:
            while 1:
                task = db.lpop(config.task_pool_key)
                if task:
                    yield task
                else:
                    gevent.sleep(config.new_task_check_time)
        else:
            #tasks = db.spop(config.task_pool_key)
            tasks = db.lpop(config.task_pool_key)
            if tasks:
                tasks = json.loads(tasks)
                for task in tasks:
                    yield task
            elif self.task_batch:
                for task in self.task_batch:
                    yield task
                del self.task_batch[:]
        #return db.smembers(config.task_pool_key)

    def init_generator(self):
        for task in self.init_tasks_generator():
            yield task

    def add_new_task(self, task):
        # need a lock if use multi thread
        if not self.rfilter.add(task['url']):  # the task has not in the filter
            if len(self.task_batch) < config.task_batch_size:
                self.task_batch.append(task)
            else:
                db = self.get_redis_connection()
                db.lpush(config.task_pool_key, json.dumps(self.task_batch))
                del self.task_batch[:]
                self.task_batch = [task]

    def flush_task_batch(self):
        if self.task_batch:
            db = self.get_redis_connection()
            db.lpush(config.task_pool_key, json.dumps(self.task_batch))
            del self.task_batch[:]

def test():
    scheduler = BaseScheduler()
    for i in scheduler.new_tasks_generator():
        print i, type(i)

if __name__ == '__main__':
    test()
