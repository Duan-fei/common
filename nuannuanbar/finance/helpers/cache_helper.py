# -*- coding:utf-8 -*-

from werkzeug.local import LocalProxy
from daisy.cache import init_memcached
from flask import current_app

_memcached = None


def _create_memecached():
    global _memcached
    if _memcached is None:
        _memcached = init_memcached(current_app)
    return _memcached


memcached = LocalProxy(_create_memecached)
