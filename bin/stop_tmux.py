#!/usr/bin/env bash

ps -ef | grep celery | grep -v grep | awk '{print $2}' | xargs kill -INT
