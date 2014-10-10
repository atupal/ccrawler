# -*- coding: utf-8 -*-

from __future__ import absolute_import
from celeryapp.celery import app
from celeryapp.celery import get_message_queue_size

from celery import group
from celery.exceptions import Retry
import datetime

import config
import celeryconfig

# registe all crawlers's task
for crawler in celeryconfig.crawlers:
    # set the crawler_name so we know the namek when parser add new task 
    # and the know call corresponding registed task
    crawler.get('requestHandler').crawler_name = crawler.get('name')
    crawler.get('parseHandler').crawler_name = crawler.get('name')
    crawler.get('scheduler').crawler_name = crawler.get('name')
    crawler.get('pipeline').crawler_name = crawler.get('name')

    # -.-.-.-.-.-.-.-.-.-.-.-.-.-.request task-.-.-.-.-.-.-.-.-.-.-.-.-.
    @app.task(name=crawler.get('name')+'.request', 
              bind=True,
              handler=crawler.get('requestHandler'),
              crawler_name=crawler.get('name'),
              rate_limit=config.rate_limit, 
              time_limit=config.time_limit,
              max_retries=config.max_retries,
              ignore_result=True)
    def request(self, dict_item, **kwargs):
        try:
            try:
                task = self.handler.handle(dict_item, **kwargs)
                if task.get('priority', None):
                    #app.tasks[self.crawler_name + '.parse_priority'].delay(task)
                    app.tasks[self.crawler_name + '.parse'].apply_async((task, ), compression='zlib', 
                        queue='parse_priority')
                else:
                    #app.tasks[self.crawler_name + '.parse'].delay(task)
                    app.tasks[self.crawler_name + '.parse'].apply_async((task, ), compression='zlib')
            except Exception as exc:
                # retry after some secends
                raise self.retry(exc=exc, countdown=config.retry_time)
        except Retry as exc: 
            pass
        except:
            # put task to new_task queue
            if 'retry_cnt' in dict_item:
              dict_item['retry_cnt'] += 1
            else:
              dict_item['retry_cnt'] = 1
            app.tasks[self.crawler_name + '.schedule'].apply_async(([dict_item], ), compression='zlib')
    # -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.

    # -.-.-.-.-.-.-.-.-.-.-.-.-.-.request_priority task-.-.-.-.-.-.-.-.-
    @app.task(name=crawler.get('name')+'.request_priority', 
              bind=True,
              handler=crawler.get('requestHandler'),
              crawler_name=crawler.get('name'),
              rate_limit=config.rate_limit, 
              time_limit=config.time_limit,
              max_retries=config.max_retries,
              ignore_result=True)
    # fake task 
    def request_priority(self, dict_item, **kwargs):
        try:
            task = self.handler.handle(dict_item, **kwargs)
            if task.get('priority', None):
                app.tasks[self.crawler_name + '.parse_priority'].delay(task)
            else:
                app.tasks[self.crawler_name + '.parse'].delay(task)
        except Exception as exc: 
            # retry after some secends
            raise self.retry(exc=exc, countdown=config.retry_time)
    # -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.

    # -.-.-.-.-.-.-.-.-.-.-.-.-.-.parse task-.-.-.-.-.-.-.-.-.-.-.-.-.-.
    @app.task(name=crawler.get('name')+'.parse', 
              bind=True, 
              handler=crawler.get('parseHandler'), 
              crawler_name=crawler.get('name'),
              ignore_result=True)
    def parse(self, dict_item, **kwargs):
        parse_result, new_tasks = self.handler.handle(dict_item, **kwargs)
        if parse_result:
            #app.tasks[self.crawler_name + '.pipeline'].delay(parse_result)
            app.tasks[self.crawler_name + '.pipeline'].apply_async((parse_result, ), compression='zlib')
        if new_tasks:
            app.tasks[self.crawler_name + '.schedule'].apply_async((new_tasks, ), compression='zlib')
        #return parse_result
        #return self.handler.handle(dict_item, **kwargs)
    # -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.

    # -.-.-.-.-.-.-.-.-.-.-.-.-.-..parse_priority task-.-.-.-.-.-.-.-.-.
    @app.task(name=crawler.get('name')+'.parse_priority',
              bind=True,
              handler=crawler.get('parseHandler'), 
              crawler_name=crawler.get('name'),
              ignore_result=True)
    # fake task
    def parse_priority(self, dict_item, **kwargs):
        parse_result, new_tasks = self.handler.handle(dict_item, **kwargs)
        if parse_result:
            app.tasks[self.crawler_name + '.pipeline'].delay(parse_result)
        if new_tasks:
            app.tasks[self.crawler_name + '.schedule'](new_tasks)
    # -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.

    # -.-.-.-.-.-.-.-.-.-.-.-.-.-.pipeline task-.-.-.-.-.-.-.-.-.-.-.-.-
    @app.task(name=crawler.get('name')+'.pipeline',
              bind=True,
              pipeline=crawler.get('pipeline'),
              crawler_name=crawler.get('name'),
              max_retries=config.max_retries,
              ignore_result=True)
    def pipeline(self, dict_item, **kwargs):
        try:
            try:
                return self.pipeline.process([dict_item], **kwargs)
            except Exception as exc:
                # retry after some secends
                raise self.retry(exc=exc, countdown=config.retry_time)
        except Retry as exc: 
            pass
        except:
            # put task to new_task queue
            print 'new retry pipe'
            app.tasks[self.crawler_name + '.pipeline'].apply_async((dict_item, ), compression='zlib')

    # -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.

    # -.-.-.-.-.-.-.-.-.-.-.-.-.-.schedule task-.-.-.-.-.-.-.-.-.-.-.-.-
    @app.task(name=crawler.get('name')+'.schedule',
              bind=True,
              scheduler=crawler.get('scheduler'),
              crawler_name=crawler.get('name'),
              ignore_result=True)
    def schedule(self, tasks=None, check_task=False, save_filter=False):
        if save_filter:
            self.scheduler.save_filter()
            return

        #  initcail tasks:
        if not tasks and not check_task:
            for task in self.scheduler.init_generator():
                if task.get('priority', None):
                    #app.tasks[self.crawler_name+'.request_priority'].delay(task)
                    app.tasks[self.crawler_name+'.request_priority'].apply_async((task, ), compression='zlib')
                else:
                    #app.tasks[self.crawler_name+'.request'].delay(task)
                    app.tasks[self.crawler_name+'.request'].apply_async((task, ), compression='zlib')
                #group(app.tasks[self.crawler_name + '.request'].s(task) 
                #        | app.tasks[self.crawler_name + '.parse'].s() 
                #        | app.tasks[self.crawler_name + '.pipeline'].s()
                #        ).delay()
            #app.tasks[self.crawler_name+'.schedule'].apply_async(
            #        args=[],
            #        kwargs = {
            #            'check_task': True,
            #            },
            #        eta=datetime.datetime.now())
        # add new tasks, call by task.apply
        elif tasks and not check_task:
            self.scheduler.add_new_task(tasks)
                #app.tasks[self.crawler_name+'.new_task'].delay(task)
        # schedule task
        elif check_task:
            #i = app.control.inspect()
            timedelta = config.new_task_check_interval
            if (get_message_queue_size('request') < config.max_task_queue_size):
                for task in self.scheduler.new_tasks_generator():
                    if task.get('priority', None):
                        app.tasks[self.crawler_name+'.request_priority'].delay(task)
                    else:
                        app.tasks[self.crawler_name+'.request'].delay(task)
                timedelta = 1
            #app.tasks[self.crawler_name+'.schedule'].apply_async(
            #        args=[],
            #        kwargs = {
            #            'check_task': True,
            #           },
            #        eta=datetime.datetime.now() + datetime.timedelta(seconds=timedelta))
    # -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.

    @app.task(name=crawler.get('name')+'.crawl_synchronous',
              bind=True,
              requestHandler =crawler.get('requestHandler'),
              parseHandler = crawler.get('parseHandler'),
              scheduler = crawler.get('scheduler'),
              pipeline = crawler.get('pipeline'),
              crawler_name=crawler.get('name'),
              rate_limit=config.rate_limit, 
              time_limit=config.time_limit,
              max_retries=config.max_retries,
              ignore_result=True,)
    def crawl_synchronous(self, dict_item, **kwargs):
        try:
            task = self.requestHandler.handle(dict_item, **kwargs)
            parse_result, new_tasks = self.parseHandler.handle(task)
            if parse_result:
                self.pipeline.process(parse_result)
            if new_tasks:
                for task in new_tasks:
                    self.scheduler.add_new_task(task)
        except Exception as exc: 
            # retry after some secends
           raise self.retry(exc=exc, countdown=config.retry_time)
