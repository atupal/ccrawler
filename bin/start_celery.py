# -*- coding: utf-8 -*-
from __future__ import absolute_import

import sys
import os
current_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_path)
root = os.path.join(current_path, '..')
sys.path.append(root)

from celeryapp.crawl_tasks import app

import socket
import logging
from random import randint
LOG = logging
def run_worker(name=None, logging_level='error',
               concurrency='100', pool='gevent',
               queue='default', sort_time_limit='10'):
    if not name:
        name = '%s_%s_%d' % (socket.getfqdn(), queue, randint(10, 99))

    argv = ['worker', 
            '-n', name,  # node name
            '-l', logging_level,
            '-P', pool,  # concurrency pool: pre_fork, thread, eventlet, gevent
            '-c', concurrency,
            '-Q', queue,
            #'--soft-time-limit', sort_time_limit,
            '-D',
            '-f', os.path.join(root, 'logs/%s.log' % name),
            '--pidfile=%s' % os.path.join(root, 'pids/%s.pid' % name)]

    app.worker_main(argv)

def run_reqeust_worker(**kwargs):
    run_worker(queue='request', **kwargs)

def run_parse_worker(**kwargs):
    run_worker(queue='parse', **kwargs)

def run_pipline_worker(**kwargs):
    run_worker(queue='pipeline', **kwargs)

def run_schedule_worker(**kwargs):
    run_worker(queue='schedule', **kwargs)

def run_all_worker():
    run_reqeust_worker()
    run_parse_worker()
    run_pipline_worker()

    # run schedul in the lastest so other worker are ready
    run_schedule_worker()

def main():
    try:
        worker = sys.argv[1]
        if worker == 'request':
            run_reqeust_worker()
        elif worker == 'parse':
            run_parse_worker()
        elif worker == 'pipeline':
            run_pipline_worker()
        elif worker == 'schedule':
            run_schedule_worker()
        else:
            LOG.error('invaid worker name!')
    except IndexError:
        run_all_worker()

if __name__ == '__main__':
    main()
