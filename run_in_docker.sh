#!/usr/bin/env bash

root=$(cd `dirname $0`; pwd)
cd $root

node=10
#node=`hostname`

queue=schedule
sudo docker run -v $PWD:/code -w /code -d centos:celery ./bin/run_queue.sh ${queue}${node}_1 ${queue} 100
sudo docker run -v $PWD:/code -w /code -d centos:celery ./bin/run_queue.sh ${queue}${node}_2 ${queue} 100
sudo docker run -v $PWD:/code -w /code -d centos:celery ./bin/run_queue.sh ${queue}${node}_3 ${queue} 100
sudo docker run -v $PWD:/code -w /code -d centos:celery ./bin/run_queue.sh ${queue}${node}_4 ${queue} 100

queue=parse
sudo docker run -v $PWD:/code -w /code -d centos:celery ./bin/run_queue.sh ${queue}${node}_1 ${queue} 100
sudo docker run -v $PWD:/code -w /code -d centos:celery ./bin/run_queue.sh ${queue}${node}_2 ${queue} 100
sudo docker run -v $PWD:/code -w /code -d centos:celery ./bin/run_queue.sh ${queue}${node}_3 ${queue} 100
sudo docker run -v $PWD:/code -w /code -d centos:celery ./bin/run_queue.sh ${queue}${node}_4 ${queue} 100

queue=pipeline
sudo docker run -v $PWD:/code -w /code -d centos:celery ./bin/run_queue.sh ${queue}${node}_1 ${queue} 100
sudo docker run -v $PWD:/code -w /code -d centos:celery ./bin/run_queue.sh ${queue}${node}_2 ${queue} 100
sudo docker run -v $PWD:/code -w /code -d centos:celery ./bin/run_queue.sh ${queue}${node}_3 ${queue} 100
sudo docker run -v $PWD:/code -w /code -d centos:celery ./bin/run_queue.sh ${queue}${node}_4 ${queue} 100

queue=request
sudo docker run -v $PWD:/code -w /code -d centos:celery ./bin/run_queue.sh ${queue}${node}_1 ${queue} 100
sudo docker run -v $PWD:/code -w /code -d centos:celery ./bin/run_queue.sh ${queue}${node}_2 ${queue} 100
sudo docker run -v $PWD:/code -w /code -d centos:celery ./bin/run_queue.sh ${queue}${node}_3 ${queue} 100
sudo docker run -v $PWD:/code -w /code -d centos:celery ./bin/run_queue.sh ${queue}${node}_4 ${queue} 100
sudo docker run -v $PWD:/code -w /code -d centos:celery ./bin/run_queue.sh ${queue}${node}_5 ${queue} 100
sudo docker run -v $PWD:/code -w /code -d centos:celery ./bin/run_queue.sh ${queue}${node}_6 ${queue} 100
sudo docker run -v $PWD:/code -w /code -d centos:celery ./bin/run_queue.sh ${queue}${node}_7 ${queue} 100
sudo docker run -v $PWD:/code -w /code -d centos:celery ./bin/run_queue.sh ${queue}${node}_8 ${queue} 100
