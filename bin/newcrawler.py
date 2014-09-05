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
eJyVVDtv2zAQ3vUrCHcgZcj00A6FUS8tUHQsmjEICEY62YwpkuYDiRG0v72k3oqCAuWi4919353u
wQ9ot92hUldCnQ4o+Hr3OWmyzWaToXj+jKdVicZo65F2g+RuLiuDtaA8M9yf0TEaaZJoJaziDZDh
zh9d+hLGaiGBsTzPIrq3GQOqGl2ftFBkTlsgTCn+b8S+A2W11Q2ycA3gPH3kDn518g+uKgkW9T/z
dWXpkIZbBy3uZ5LeQc31HcaVZ6iC7GB3/WWBGZUdoOKeJ98ujjAghYJFjF6XDbX3ooFBjmiY35+c
Vh3vo/s0sgAPXtRB3ulgsqyU3Dm0/GGyrkF+aCehghqdWw1xIOsCee4uBQoOmLH65Xb8zqWDAm23
l2duT66HpZM842C4YGKAJXmBEllOe+bkmY84Cz5Y1cKHbOeFJm8r/69MZ+nYmEtS3WMLzmjlAD+M
RhdLE+2LUhFLPbz4Am3kSyM3U4IKnllichFxP3GIuucPVrIKjD/jB/QFfZxSSKfWFsV+XpBQbVRa
C1UxLiXBHOdL35bVQxPjvCZWfGih9ASe4LOFGudx4Kdwh3UCv1eEY/bDMqUI71a/mHyHRozTSxaz
PGvBCRRY7rVtu7Aeh9dVQv2f4bP35rDfX6+01A1euU1/chMgq+V89EtC5hszSyqOagnO9YMR+x+k
n49qaopNHelNyzYkFDVWxDemsxMbX5fYbsbSU8cYOh4RZqzhQjGGO3C3hUJR53nbYK2A2aDmu/3N
8uf0EiT/spPTEE6WN2tDYrsXqxDvU0eScahDns9JaYxL8uwvzejo6Q==
""")

def main():
    args = parser.parse_args()
    print args.name

if __name__ == '__main__':
    main()
