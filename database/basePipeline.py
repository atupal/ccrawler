# -*- coding: utf-8 -*-
'''
    basePipeline.py
    ~~~~~~~~~~~~~~~
'''
import logging
import redis

try:
    from pymongo import MongoClient
    from pymongo import ReadPreference
    import couchdb
except:
    pass
 
class BasePipeline(object):
    def __init__(self, ):
        self._redis_db = None
        self._mongo_db = None
        self.crawler_name = 'unset'

    def process(self, results):
        for r in results:
            logging.info(str(r)[:10])

    def get_redis_db(self):
        if not self._redis_db:
            import config
            redis_connection = redis.ConnectionPool(
                    host=config.redis_server_host,
                    port=config.redis_server_port,
                    db=config.redis_job_db,
            )
            self._redis_db = redis.Redis(connection_pool=redis_connection)
        return self._redis_db

    def get_mongo_db(self):
        if not self._mongo_db:
            import config
            mongo_connection = MongoClient(
                    '%s:%d' % (
                        config.mongo.get('host'), config.mongo.get('port')
                        ),
                    read_preference=ReadPreference.SECONDARY,
                    max_pool_size=10, use_greenlets=True
                    )
            self._mongo_db = getattr(mongo_connection, config.mongo.get('db'))
        return self._mongo_db


    def save_to_redis(self, result):
        redis_db = self.get_redis_db()

    def save_to_mongo(self, result):
        mongo_db = sefl.get_mongo_db()

    def save_to_file(self, result):
        pass

    def save_to_kafka(self, result):
        pass

    def save_to_couchdb(self, result):
        if not hasattr(self, 'couch'):
            import config
            self.couch = couchdb.Server(config.couchdb)
        db = self.couch['weibo']
        db.save(result)

    def print_result(self, result, l=1024):
        print ('%s crawler:' % self.crawler_name + '\033[31m' + str(result)[:l] + 
                ('\033[0m' if len(str(result)) < l else '...(more)\033[0m'))

def test():
    pipeline = BasePipeline()

if __name__ == '__main__':
    test()
