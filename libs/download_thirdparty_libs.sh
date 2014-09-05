#!/usr/bin/env bash

current_dir=$(cd `dirname $0`; pwd)
cd current_dir

# download ssdb
wget https://github.com/ideawu/ssdb/archive/master.zip
unzip master.zip
rm -rf master.zip
