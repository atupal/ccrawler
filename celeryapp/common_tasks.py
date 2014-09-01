# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os, sys
root = os.path.dirname(os.path.abspath(__file__))

from celeryapp.celery import app
from celery import group

import config
import celeryconfig

@app.task
def add(x, y):
    return x+y
