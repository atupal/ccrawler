#!/usr/bin/env bash
root=$(cd `dirname $0`; pwd)
cd "$root/.."
tmux split-window -h \
    "celery -A celeryapp worker -l info -c 100 -P gevent --soft-time-limit 10 --without-gossip  -n schedule -Q schedule"

declare -A arr

arr["pipeline"]=50
#arr["parse_priority"]=100
arr["parse"]=250
#arr["request_priority"]=100
arr["request"]=500

cnt=6
for key in ${!arr[@]}; do
    ((cnt=cnt-1))
    ((size=cnt*9))
    tmux split-window -l $size \
        "celery -A celeryapp worker -l info -c ${arr[$key]} -P gevent --without-gossip  -n $key -Q $key"
done
