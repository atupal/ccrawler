#!/usr/bin/env bash

current_dir=$(cd `dirname $0`; pwd)
cd current_dir

# download ssdb
if [ ! -d "$current_dir/ssdb-master" ]; then
  wget https://github.com/ideawu/ssdb/archive/master.zip
  unzip master.zip
  rm -rf master.zip
fi

# download docker-nsenter
if [ ! -d "$current_dir/nsenter-master" ]; then
  wget https://github.com/jpetazzo/nsenter/archive/master.zip
  unzip master.zip
  rm -rf master.zip
fi
