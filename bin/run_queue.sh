#!/usr/bin/env bash

C_FORCE_ROOT=1 celery -A celeryapp worker -l info -c $3 -P gevent --soft-time-limit 10 --without-gossip  -n $1 -Q $2
