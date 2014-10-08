#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

import argparse
import base64
import zlib
import StringIO

parser = argparse.ArgumentParser(description='genera a clrawlr template')
parser.add_argument('name')

def convert(s):
    b = base64.b64decode(s.encode('ascii'))
    return zlib.decompress(b).decode('utf-8')

def compress(filepath):
    ret = StringIO.StringIO()
    l = 76
    with open(filepath) as fi:
        text = fi.read()
        z = zlib.compress(text.encode('utf-8'))
        s = base64.b64encode(z).decode('ascii')
        for i in xrange(len(s)/l+1):
            print >>ret, s[i*l:(i+1)*l]
    retstring = ret.getvalue()
    ret.close()
    return retstring

TEMPLATE_CRAWLER = convert("""
eJyVVMtq3DAU3fsrxHQhOTgOlC7K0Nm0ULoszTIEodjXM0pkSdGDmSG0394rv50ZCvXGku4596Vz
9YHc3tySytRS77ckhub2czrJNptNRvCDk2itgtKeu+2f6esQsrXGBWL8uPJnn1XROdCBWxEOZIfG
Mq3KWjotWmDjXjz59GecN1IB53meIXuwWQu6nqDPRmq2dFsQWpb0vxl3PSlrnGmJg9cIPpRPwsOv
fv1D6FqBI0MxXy8sPdMK56Hj/UyrK6zlec/x1QHqqHra/bBZcabDnlCLIBK2jyMtKKlhFWM4y8be
B9nCuEY2LPfP3uje75P/NHkBEYNsoro30WZZpYT3ZF0wu+xBvu2UUENDDt0J86CaggThXwoSPXDr
zOm8+y6Uh4Lc3Lwchdv7gZa+hERh+GgxwNp5QZKzvBw8J2Q+8RyE6HRHH7NdNpq97/y/Ml2k4zCX
dPRAHXhrtAf6+EArowOKhz5OOI9dQuiqawwz3qhTqzZzmhqOPPnzCH6Y6bIZokSneA02HOgj+UI+
zomkrzGO4K2+EKm7gGUjdc2FUowKmq+xg9cEL/cQGD04aCgqnealD8IFf5Q4YPQQgqU5wRYQbcJ1
PA7PgIYTXAvUBQvQYlFvqQS6fe8oR09zbdvLan9fdTq1a5zhFOXqpRczdrz/aWjYaoQWNy+1DHwP
GpwIxnUKuJTi20VmQ4ld77Z3d6+vZWVaWlzg5prOElS9FucwoWw5rovUcE4q8H5QJYovqrCck6QF
l4QwmNaXklildRIfuN7OXL4CWMwBH4eGcJ4eXs7Jbkco562QmnPae+vfBKmTYDqhGQ3cRb18ab45
cUzvUsJX/TrNwWx5N8QMlbAaTNzPF5WMY2PyfOm0xLgsz/4Cf7kUfA==
""")

def main():
    args = parser.parse_args()
    print '\033[31m', 'generating crawler: %s' % args.name, '\033[0m'
    with open(os.path.join(root, 'crawlers/%s.py' % args.name), 'w') as fi:
        fi.write(TEMPLATE_CRAWLER)

if __name__ == '__main__':
    main()
