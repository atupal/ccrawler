## weibo

crawler.py 中几个函数：
- `get_friends`: 获取关注列表，新任务也是从这个函数里产生的，把关注列表里的所有 uid 加到任务队列中去
- `get_profile`: 获取 个人资料
- `get_timeline`: 获取 最近 100 条微博并根据这一百条微博 计算 tag 和 活跃率
- `get_tag`： 或缺用户自己贴的标签

这四个函数依据 task 中 type 的参数响应的执行。存储是分开存的，俊以json格式存成文档，均还含有 uid 参数。

存在 couchdb 中：

## couchdb
couchdb 启动方式：
```sh
couchdb -d
```

couchdb stop：
```sh
couchdb -k
```

couchdb 数据目录：
```
/data
/data1
```
目前 data1 是活跃目录

couchdb web 面板： http://127.0.0.1:5984/_utils

## machine

- degreedocker10 中心节点，爬虫在这个节点上启动
- degreedocker11 爬取节点
- degreedocker12 爬取节点

启动方法：

先启动 redis，ssdb ，couchdb, ssdb 在 ./libs/ssdb-master 目录下
然后在docker 里面运行 request，parse，pipeline，schedule 队列，见 https://github.com/atupal/ccrawler/blob/master/run_in_docker.sh

最后在中心节点上启动 ./bin/run.py
docker 对应的命令： `docker run -v $PWD:/code -w /code -d centos:celery python2.7 ./bin/run.py`
