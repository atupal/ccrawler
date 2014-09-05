#!/usr/bin/env bash

root=$(cd `dirname $0`; pwd)
cd $root

sudo docker run -t -i -v $PWD:/code -w /code centos:celery $@
