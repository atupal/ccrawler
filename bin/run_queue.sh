#!/usr/bin/env bash

# no -l info
C_FORCE_ROOT=1 exec celery -A celeryapp worker  -c $3 -P gevent --soft-time-limit 10 --without-gossip  -n $1 -Q $2
