# -*- coding: utf-8 -*-

'''
    baseScheduler.py
    ~~~~~~~~~~~~~~~~
'''
import os
import sys
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
root = os.path.abspath(root)
sys.path.append(root)

import config
import redis
import gevent
import json
import time
from redisfilter import ScalableRedisBloomFilter, ScalableBloomFilter
from gevent.lock import Semaphore

class BaseScheduler(object):
    def __init__(self, ):
        # redis or ssdb
        self.redis_connection_pool = redis.ConnectionPool(
                host=config.tasks_pool.get('host') or '127.0.0.1',
                port=config.tasks_pool.get('port') or 6379,
                db=config.tasks_pool.get('db') or 0,
                )
        self.task_batch = []
        self.add_new_task_lock = Semaphore()
        self.rfilter_lock = Semaphore()
        if config.multi_scheduler:
            self.rfilter = ScalableRedisBloomFilter(
                    initial_capacity=100000000, error_rate=0.0001,
                    connection=redis.Redis(host=config.rfilter_redis),
                    prefixbitkey='ccrawler', clear_filter=True)
        else:
            # create filter lazily
            self.rfilter = None

        self.filter_unsaved_count = 0
        self.filter_file_name = 'filter.dat'


    def get_redis_connection(self):
        return redis.Redis(connection_pool=self.redis_connection_pool)

    def create_filter(self):
        print 'creating filter....'
        st = time.time()
        filepath = os.path.join(root, 'data/%s' % self.filter_file_name)
        if os.path.exists(filepath):
            print 'reading filter from file'
            with open(filepath, 'rb') as f:
                rfilter = ScalableBloomFilter.fromfile(f)
        else:
            rfilter = ScalableBloomFilter(100000000, 0.0001)
        print 'creating filter end. use %fs' % (time.time() - st)
        return rfilter

    def save_filter(self):
        if self.rfilter:
            print 'saving filter.....'
            st = time.time()
            filepath = os.path.join(root, 'data/%s' % self.filter_file_name)
            #if os.path.exists(filepath):
            #    comfire = raw_input("Overwrite the filter file?[yes/no]:")
            #    if not comfire.strip().lower() == 'yes':
            #        return
            with self.rfilter_lock:
                with open(filepath+'.tmp', 'wb') as f:
                    self.rfilter.tofile(f)
                os.rename(filepath+'.tmp', filepath)
            print 'saving filter end. use %fs' % (time.time() - st)

    def init_tasks_generator(self):
        raise NotImplementedError

    def add_to_filter(self, uuid):
        exist = False
        if not self.rfilter:
            with self.rfilter_lock:
                self.rfilter = self.create_filter()

        if config.multi_scheduler:
            with self.rfilter_lock:
                exist = self.rfilter.add(uuid)
        else:
            exist = self.rfilter.add(uuid)

        if not exist:
            self.filter_unsaved_count += 1
            if config.save_filter_interval != -1 and self.filter_unsaved_count >= config.save_filter_interval:
                self.save_filter()
                self.filter_unsaved_count = 0

        return exist

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
            else:
                tasks = self.task_batch
                self.task_batch = []

            for task in tasks:
                # need a lock if use multi thread
                uuid = task.get('uuid', None) or task['url']

                
                in_filter = self.add_to_filter(uuid)

                if not in_filter:
                    yield task

            return
        #return db.smembers(config.task_pool_key)

    def init_generator(self):
        for task in self.init_tasks_generator():
            yield task

    #def add_new_task(self, task, uuid=None):
    #    # need a lock if use multi thread
    #    if not uuid:
    #        uuid = task['url']
    #    if not self.rfilter:
    #        with self.rfilter_lock:
    #            self.rfilter = self.create_filter()
    #    if config.multi_scheduler:
    #        with self.rfilter_lock:
    #            in_filter = self.rfilter.add(uuid)
    #    else:
    #        in_filter = self.rfilter.add(uuid)
    #    if not in_filter:  # the task has not in the filter
    #        with self.add_new_task_lock:
    #            if len(self.task_batch) < config.task_batch_size: self.task_batch.append(task)
    #            else:
    #                db = self.get_redis_connection()
    #                db.lpush(config.task_pool_key, json.dumps(self.task_batch))
    #                del self.task_batch[:]
    #                self.task_batch = [task]

    def add_new_task(self, task_or_tasks):
        task = task_or_tasks

        with self.add_new_task_lock:
            if isinstance(task, list):
                for t in task:
                    if len(self.task_batch) < config.task_batch_size:
                        self.task_batch.append(t)
                    else:
                        db = self.get_redis_connection()
                        try:
                            db.lpush(config.task_pool_key, json.dumps(self.task_batch))
                        except:
                            pass
                        self.task_batch = [t]
            else:
                if len(self.task_batch) < config.task_batch_size:
                    self.task_batch.append(task)
                else:
                    db = self.get_redis_connection()
                    db.lpush(config.task_pool_key, json.dumps(self.task_batch))
                    del self.task_batch[:]
                    self.task_batch = [task]

    def flush_task_batch(self):
        if self.task_batch:
            with self.add_new_task_lock:
                db = self.get_redis_connection()
                db.lpush(config.task_pool_key, json.dumps(self.task_batch))
                del self.task_batch[:]

def test():
    scheduler = BaseScheduler()
    def add_new_task(task):
        scheduler.add_new_task(task)

    import sys
    if 'threading' in sys.modules:
        del sys.modules['threading']
    from gevent import monkey
    monkey.patch_all()
    from gevent.pool import Pool
    gp = Pool(100)
    import time
    st = time.time()
    tasks = []
    for i in xrange(1, 1000):
        t = {
            'uuid': i
            }
        tasks.append(t)
    gp.spawn(add_new_task, tasks)
    gp.join()

    end = time.time()
    tmp = list(iter(scheduler.new_tasks_generator()))
    cnt = len(tmp)
    while tmp:
    #for i in xrange(1000):
        tmp = list(iter(scheduler.new_tasks_generator()))
        cnt += len(tmp)

    print [ i in scheduler.rfilter for i in xrange(1, 1000) ]
    print [ i in scheduler.rfilter for i in xrange(1000, 1500) ]
    print cnt
    print end - st
    print time.time() - st
    #scheduler.save_filter()

if __name__ == '__main__':
    test()
    #import cProfile
    #cProfile.run('test()')
