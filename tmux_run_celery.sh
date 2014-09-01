#!/usr/bin/env bash

tmux split-window -h \
    "celery -A celeryapp worker -l info -c 100 -P gevent --soft-time-limit 10 --without-gossip  -n schedule -Q schedule"
cnt=6
for queue in request request_priority parse parse_priority pipeline ; do
    ((cnt=cnt-1))
    ((size=cnt*9))
    tmux split-window -l $size \
        "celery -A celeryapp worker -l info -c 100 -P gevent --soft-time-limit 10 --without-gossip  -n $queue -Q $queue"
done
