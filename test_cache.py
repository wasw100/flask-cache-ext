#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement

import sys
import os
import random

from flask import Flask
from flask_cache._compat import PY2
from flask_cache_ext import Cache

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class CacheTestCase(unittest.TestCase):

    def _set_app_config(self, app):
        app.config['CACHE_TYPE'] = 'simple'

    def setUp(self):
        app = Flask(__name__, template_folder=os.path.dirname(__file__))

        app.debug = True
        self._set_app_config(app)

        self.cache = Cache(app)

        self.app = app

    def tearDown(self):
        self.app = None
        self.cache = None
        self.tc = None

    def test_05_cached_function(self):
        with self.app.test_request_context():
            @self.cache.memoize()
            def func(a):
                return random.randrange(0, 100000)

            k1 = func.make_cache_key(func.uncached, 1)
            k2 = func.make_cache_key(func.uncached, 2)
            k3 = func.make_cache_key(func.uncached, '1')
            assert k1 != k2
            assert k1 == k3
            if PY2:
                k4 = func.make_cache_key(func.uncached, u'1')
                k5 = func.make_cache_key(func.uncached, long(1))
                assert k1 == k4
                assert k1 == k5


if __name__ == '__main__':
    unittest.main()
