#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
    baseCrawler.py
    ~~~~~~~~~~~~~~

    Base class of crawler, run in stand alone mode
"""
import gevent
import sys
from gevent import monkey 
if 'threading' in sys.modules:
        del sys.modules['threading']
monkey.patch_all()
import collections
import logging
import os
import thread
import time
from exceptions import NotImplementedError
from gevent.pool import Pool
from gevent.queue import JoinableQueue
from requests.exceptions import ConnectionError
from requests.exceptions import ProxyError

current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_path, '..'))

import config
from request.baseRequestHandler import BaseRequestHandler
from parse.baseParseHandler import BaseParseHandler
from schedule.baseScheduler import BaseScheduler
from database.basePipeline import BasePipeline

class BaseCrawler(object):
    def __init__(self, requestHandler=BaseRequestHandler(),
                       parseHandler=BaseParseHandler(),
                       sheduler=BaseScheduler(),
                       pipeline=BasePipeline()):
        self.requestHandler = requestHandler
        self.parseHandler = parseHandler
        self.sheduler = sheduler
        self.pipeline = pipeline
        self.task_queue = JoinableQueue()
        self.response_queue = JoinableQueue()
        self.tasks_cnt = 0
        self.result_queue = JoinableQueue()
        self.jobs_cnt = config.num_threads
        self.start_time = time.time()
        self.stop = False
    
    def doScheduler(self):
        """Generate tasks, one thread
        """
        logging.info('scheduler started!')
        for task in self.sheduler.init_generator():
            self.task_queue.put(task)
            self.tasks_cnt += 1

        while self.tasks_cnt > 0 and not self.stop:
            gevent.sleep(config.new_task_check_time)

        logging.info('scheduler finished! All task done.')

        for i in xrange(config.num_threads):
            self.task_queue.put(StopIteration)

    def worker(self):
        """Fetch url and parse, config.num_threads threads
        """
        task = self.task_queue.get()
        cnt = config.error_retry_cnt
        while task != StopIteration:
            try:
                #timeout = gevent.Timeout(config.TASK_TIMEOUT)
                #timeout.start()
                response = self.requestHandler.handle(task)
                result, new_tasks = self.parseHandler.handle(response)
                #timeout.cancel()
                #if isinstance(result, collections.Iterable):
                #if isinstance(result, list):
                #    for ret in result:
                #        self.result_queue.put(ret)
                #else:
                if result:
                    self.result_queue.put(result)
                for task in new_tasks:
                    self.task_queue.put(task)
                    self.tasks_cnt += 1
                #self.task_queue.task_done()
                self.tasks_cnt -= 1
                task = self.task_queue.get()
                cnt = config.error_retry_cnt
            except Exception as e:
                try:
                    #timeout.cancel()
                    cnt -= 1
                    logging.exception(e)
                    if cnt <= 0:
                        #self.task_queue.task_done()
                        self.tasks_cnt -= 1
                        task = self.task_queue.get()
                        logging.error('task failed, try \033[31m%d\033[0m times! will not try' % (config.error_retry_cnt - cnt))
                        cnt = config.error_retry_cnt
                    #logging.exception('task failed!')
                    else:
                        logging.error('task failed, try \033[31m%d\033[0m times!' % (config.error_retry_cnt - cnt))
                except Exception as e:
                    self.tasks_cnt -= 1
                    #self.jobs_cnt -= 1
                    raise
            finally:
                #timeout.cancel()
                pass
        self.jobs_cnt -= 1

    def doPipeline(self):
        while self.jobs_cnt > 0 or not self.result_queue.empty():
            gevent.sleep(config.pipeline_sleeptime)
            results = []
            try:
                while 1:
                    results.append(self.result_queue.get_nowait())
                    if len(results) > 100:
                        raise gevent.queue.Empty
            except gevent.queue.Empty:
                if results:
                    try:
                        self.pipeline.process(results)
                    except:
                        logging.exception('')
                #logging.exception('')
            except:
                logging.exception('')

    def run(self):
        jobs = [
                gevent.spawn(self.doScheduler),
                gevent.spawn(self.doPipeline),
                ]
        for i in xrange(config.num_threads):
            job = gevent.spawn(self.worker)
            jobs.append(job)
            #thread.start_new_thread(self.worker)
        try:
            timeout = gevent.Timeout(config.CRAWLER_TIMEOUT)
            timeout.start()
            #self.task_queue.join()
            gevent.joinall(jobs)
        except:
            logging.exception('pipeline error!')
        finally:
            timeout.cancel()
            self.end_time = time.time()
            logging.info('run times: %f s' % (self.end_time - self.start_time))

def test():
    from crawlers.weibo.crawler import RequestHandler, ParseHandler, Scheduler, Pipeline
    crawler = BaseCrawler(RequestHandler(), ParseHandler(), Scheduler(), Pipeline())
    crawler.run()
    
if __name__ == '__main__':
    test()
