# -*- coding: utf-8 -*-
from crawlers import example
from crawlers import github
from crawlers.weibo import crawler as weibo

crawlers = [
        #{
        #    'name': 'example',
        #    'requestHandler': example.RequestHandler(),
        #    'parseHandler': example.ParseHandler(),
        #    'scheduler': example.Scheduler(),
        #    'pipeline': example.Pipeline(),
        #},
        #{
        #    'name': 'github',
        #    'requestHandler': github.RequestHandler(use_proxy=0),
        #    'parseHandler': github.ParseHandler(),
        #    'scheduler': github.Scheduler(),
        #    'pipeline': github.Pipeline(),
        #},
        {
            'name': 'weibo',
            'requestHandler': weibo.RequestHandler(use_proxy=0),
            'parseHandler': weibo.ParseHandler(),
            'scheduler': weibo.Scheduler(),
            'pipeline': weibo.Pipeline(),
        },
    ]

from kombu import Queue, Exchange

CELERY_QUEUES = (
    Queue('request', Exchange('request'), routing_key='request'),
    Queue('request_priority', Exchange('request_priority'), routing_key='request_priority'),
    Queue('parse', Exchange('parse'), routing_key='parse'),
    Queue('parse_priority', Exchange('parse_priority'), routing_key='parse_priority'),
    Queue('pipeline', Exchange('pipeline'), routing_key='pipeline'),
    Queue('schedule', Exchange('schedule'), routing_key='schedule'),
)

CELERY_ROUTES = {}
CELERY_ROUTES.update({
        '%s.request' % crawler['name']: {
            'queue': 'request',
            'routing_key': 'request',
            } for crawler in crawlers})
CELERY_ROUTES.update({
        '%s.request_priority' % crawler['name']: {
            'queue': 'request_priority',
            'routing_key': 'request_priority',
            } for crawler in crawlers})
CELERY_ROUTES.update({
        '%s.parse' % crawler['name']: {
            'queue': 'parse',
            'routing_key': 'parse',
            } for crawler in crawlers})
CELERY_ROUTES.update({
        '%s.parse_priority' % crawler['name']: {
            'queue': 'parse_priority',
            'routing_key': 'parse_priority',
            } for crawler in crawlers})
CELERY_ROUTES.update({
        '%s.pipeline' % crawler['name']: {
            'queue': 'pipeline',
            'routing_key': 'pipeline',
            } for crawler in crawlers})
CELERY_ROUTES.update({
        '%s.schedule' % crawler['name']: {
            'queue': 'schedule',
            'routing_key': 'schedule',
            } for crawler in crawlers})

#from datetime import timedelta
#CELERYBEAT_SCHEDULE = {
#        'crawl-%sjob-every-30-min' % crawler['name']: {
#            'task': '%s.schedule' % crawler['name'],
#            'schedule': timedelta(minutes=30),
#            } for crawler in crawlers
#        }
#CELERY_TIMEZONE = 'UTC'
