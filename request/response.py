# -*- coding: utf-8 -*-
"""
    response.py
    ~~~~~~~~~~~
"""

class Response(object):

    def __init__(self, resp):
        if not hasattr(resp, 'content'):
            raise ValueError('resp has no content attr!')
        self.content = resp.content
