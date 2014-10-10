#!/usr/bin/env bash

#rsync -avzhe ssh ./ 37degree@degreedocker10.cloudapp.net:3344:/home/37degree/ccrawler
#scp -P 3344 ./ccrawler.tar.gz 37degree@degreedocker10.cloudapp.net:/home/37degree/
#scp -P 3344 ./ccrawler.tar.gz 37degree@degreedocker11.cloudapp.net:/home/37degree/
#scp -P 3344 ./ccrawler.tar.gz 37degree@degreedocker12.cloudapp.net:/home/37degree/

rsync -avzhe "ssh -p 3344" ./ 37degree@degreedocker10.cloudapp.net:/home/37degree/ccrawler --exclude '.git' --exclude libs/ssdb-master  --exclude libs/nsenter-master
rsync -avzhe "ssh -p 3344" ./ 37degree@degreedocker11.cloudapp.net:/home/37degree/ccrawler --exclude '.git' --exclude libs/ssdb-master  --exclude libs/nsenter-master
rsync -avzhe "ssh -p 3344" ./ 37degree@degreedocker12.cloudapp.net:/home/37degree/ccrawler --exclude '.git' --exclude libs/ssdb-master  --exclude libs/nsenter-master
