# -*- coding: utf-8 -*-
"""
    filter.py
    ~~~~~~~~~
"""

from __future__ import absolute_import
import math
import sys
try:
    import StringIO
    import cStringIO
except ImportError:
    from io import BytesIO
import hashlib
from struct import unpack, pack, calcsize

from pybloom import BloomFilter, ScalableBloomFilter

running_python_3 = sys.version_info[0] == 3

def range_fn(*args):
    if running_python_3:
        return range(*args)
    else:
        return xrange(*args)


def is_string_io(instance):
    if running_python_3:
       return isinstance(instance, BytesIO)
    else:
        return isinstance(instance, (StringIO.StringIO,
                                     cStringIO.InputType,
                                     cStringIO.OutputType))

def make_hashfuncs(num_slices, num_bits):
    if num_bits >= (1 << 31):
        fmt_code, chunk_size = 'Q', 8
    elif num_bits >= (1 << 15):
        fmt_code, chunk_size = 'I', 4
    else:
        fmt_code, chunk_size = 'H', 2
    total_hash_bits = 8 * num_slices * chunk_size
    if total_hash_bits > 384:
        hashfn = hashlib.sha512
    elif total_hash_bits > 256:
        hashfn = hashlib.sha384
    elif total_hash_bits > 160:
        hashfn = hashlib.sha256
    elif total_hash_bits > 128:
        hashfn = hashlib.sha1
    else:
        hashfn = hashlib.md5
    fmt = fmt_code * (hashfn().digest_size // chunk_size)
    num_salts, extra = divmod(num_slices, len(fmt))
    if extra:
        num_salts += 1
    salts = tuple(hashfn(hashfn(pack('I', i)).digest()) for i in range_fn(num_salts))
    def _make_hashfuncs(key):
        if running_python_3:
            if isinstance(key, str):
                key = key.encode('utf-8')
            else:
                key = str(key).encode('utf-8')
        else:
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            else:
                key = str(key)
        i = 0
        for salt in salts:
            h = salt.copy()
            h.update(key)
            for uint in unpack(fmt, h.digest()):
                yield uint % num_bits
                i += 1
                if i >= num_slices:
                    return

    return _make_hashfuncs

class RedisBloomFilter(object):

    def __init__(self, capacity, error_rate=0.001,
                       connection=None, 
                       bitkey='bloom_filter', clear_filter=False):
        if not (0 < error_rate < 1):
            raise ValueError("Error_Rate must be between 0 and 1.")
        if not capacity > 0:
            raise ValueError("Capacity must be > 0")
        self.capacity = capacity
        self.error_rate = error_rate

        self.connection = connection
        if not self.connection:
            import redis
            self.connection = redis.Redis()
        self.bitkey = bitkey
        if clear_filter:
            self.connection.delete(self.bitkey)

        num_slices = int(math.ceil(math.log(1.0 / error_rate, 2)))
        bits_per_slice = int(math.ceil(
            (capacity * abs(math.log(error_rate))) /
            (num_slices * (math.log(2) ** 2))))
        self._setup(error_rate, num_slices, bits_per_slice, capacity, 0)

    def _setup(self, error_rate, num_slices, bits_per_slice, capacity, count):
        self.error_rate = error_rate
        self.num_slices = num_slices
        self.bits_per_slice = bits_per_slice
        self.capacity = capacity
        self.num_bits = num_slices * bits_per_slice
        self.count = count
        self.make_hashes = make_hashfuncs(self.num_slices, self.bits_per_slice)

    def __contains__(self, key):
        """Tests a key's membership in this bloom filter.

        >>> b = BloomFilter(capacity=100)
        >>> b.add("hello")
        False
        >>> "hello" in b
        True

        """
        bits_per_slice = self.bits_per_slice
        pipeline = self.connection.pipeline(transaction=False)
        hashes = self.make_hashes(key)
        offset = 0
        for k in hashes:
            pipeline.getbit(self.bitkey, offset+k)
            offset += bits_per_slice
        results = pipeline.execute()
        #print (iter(hashes)), results
        return all(results)

    def __len__(self):
        """Return the number of keys stored by this bloom filter."""
        return self.count

    def add(self, key):
        """ Adds a key to this bloom filter. If the key already exists in this
        filter it will return True. Otherwise False.

        >>> b = BloomFilter(capacity=100)
        >>> b.add("hello")
        False
        >>> b.add("hello")
        True
        >>> b.count
        1

        """
        if key in self:
            return True
        self.count += 1
        pipeline = self.connection.pipeline(transaction=False)
        bits_per_slice = self.bits_per_slice
        hashes = self.make_hashes(key)
        found_all_bits = True
        if self.count > self.capacity:
            raise IndexError("BloomFilter is at capacity")
        offset = 0
        for k in hashes:
            pipeline.setbit(self.bitkey, offset + k, 1)
            offset += bits_per_slice
        pipeline.execute()
        return False

    def __getstate__(self):
        d = self.__dict__.copy()
        del d['make_hashes']
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
        self.make_hashes = make_hashfuncs(self.num_slices, self.bits_per_slice)

class ScalableRedisBloomFilter(object):
    SMALL_SET_GROWTH = 2 # slower, but takes up less memory
    LARGE_SET_GROWTH = 4 # faster, but takes up more memory faster

    def __init__(self, initial_capacity=1000, error_rate=0.001,
                       connection=None, 
                       prefixbitkey='scalable_bloom_filter', clear_filter=False,
                       mode=SMALL_SET_GROWTH):
        if not error_rate or error_rate < 0:
            raise ValueError("Error_Rate must be a decimal less than 0.")
        if not initial_capacity > 0:
            raise ValueError("Capacity must be > 0")

        self.connection = connection
        if not self.connection:
            import redis
            self.connection = redis.Redis()
        self.prefixbitkey = prefixbitkey
        self.clear_filter = clear_filter

        self._setup(mode, 0.9, initial_capacity, error_rate)
        self.filters = []

    def _setup(self, mode, ratio, initial_capacity, error_rate):
        self.scale = mode
        self.ratio = ratio
        self.initial_capacity = initial_capacity
        self.error_rate = error_rate

    def __contains__(self, key):
        for f in reversed(self.filters):
            if key in f:
                return True
        return False

    def add(self, key):
        if key in self:
            return True
        if not self.filters:
            filter = RedisBloomFilter(
                self.initial_capacity,
                error_rate=self.error_rate * (1.0 - self.ratio),
                connection=self.connection,
                bitkey='%s_%d' % (self.prefixbitkey, len(self.filters)+1),
                clear_filter=self.clear_filter
                )
            self.filters.append(filter)
        else:
            filter = self.filters[-1]
            if filter.count >= filter.capacity:
                filter = RedisBloomFilter(
                    filter.capacity * self.scale,
                    error_rate=filter.error_rate * self.ratio,
                    connection=self.connection,
                    bitkey='%s_%d' % (self.prefixbitkey, len(self.filters)+1),
                    clear_filter=self.clear_filter)
                self.filters.append(filter)
        filter.add(key)
        return False

    @property
    def capacity(self):
        """Returns the total capacity for all filters in this SBF"""
        return sum(f.capacity for f in self.filters)

    @property
    def count(self):
        return len(self)

    def __len__(self):
        """Returns the total number of elements stored in this SBF"""
        return sum(f.count for f in self.filters)

def test():
    scalablef = ScalableRedisBloomFilter(initial_capacity=100000000, error_rate=0.001, prefixbitkey='test', clear_filter=True)
    f = RedisBloomFilter(400000000, error_rate=0.01, bitkey='test', clear_filter=True)
    keys_in = []
    keys_notin = []
    from uuid import uuid4
    for i in range_fn(500):
        keys_in.append(str(uuid4()))
    for i in range_fn(500):
        keys_notin.append(str(uuid4()))

    for key in keys_in:
        scalablef.add(key)
        f.add(key)

    print ([ key in scalablef for key in keys_in ])
    print ([ key in scalablef for key in keys_notin ])
    print ([ key in f for key in keys_in ])
    print (([ key in f for key in keys_notin ]))

def test_gevent():
    f = ScalableRedisBloomFilter(initial_capacity=100000000, error_rate=0.0001, prefixbitkey='test_gevent', clear_filter=True)

    def add_key(key):
        with lock:
            f.add(key)

    import gevent
    import sys
    if 'threading' in sys.modules:
        del sys.modules['threading']
    from gevent import monkey
    monkey.patch_all()
    from gevent.pool import Pool
    from gevent.lock import Semaphore
    lock = Semaphore()
    gp = Pool(100)
    import time
    st = time.time()
    for i in xrange(1000):
        gp.spawn(add_key, i)
    gp.join()
    print time.time() - st
    print [ i in f for i in xrange(1000) ]
    print [ i in f for i in xrange(1000, 1500) ]

def test_pybloom():
    from pybloom import BloomFilter, ScalableBloomFilter
    f = ScalableRedisBloomFilter(100000000, 0.0001)
    import time
    st = time.time()
    for i in xrange(1000):
        f.add(i)
    print time.time() - st
    print [ i in f for i in xrange(1000) ]
    print [ i in f for i in xrange(1000, 2000) ]

def test_gevnet_pybloom():
    from pybloom import BloomFilter, ScalableBloomFilter
    f = ScalableRedisBloomFilter(100000000, 0.0001)

    def add_key(key):
        with lock:
            f.add(key)

    import gevent
    import sys
    if 'threading' in sys.modules:
        del sys.modules['threading']
    from gevent import monkey
    monkey.patch_all()
    from gevent.pool import Pool
    from gevent.lock import Semaphore
    lock = Semaphore()
    gp = Pool(100)
    import time
    st = time.time()
    for i in xrange(1000):
        gp.spawn(add_key, i)
    gp.join()
    print time.time() - st
    print [ i in f for i in xrange(1000) ]
    print [ i in f for i in xrange(1000, 2000) ]

if __name__ == '__main__':
    #test()
    #test_gevent()
    #test_pybloom()
    test_gevnet_pybloom()
