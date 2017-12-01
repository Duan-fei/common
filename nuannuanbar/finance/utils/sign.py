#!/usr/bin/env python
# -*- coding: utf-8
__author__ = 'zjw'

import hashlib


def key_sort(data):
    """
    sort by dict key and return sorted list

    :param data:  dict to sort
    :type data: dict
    :return: sorted list of k,v tuple
    :rtype: list
    """
    return [(k, data[k]) for k in sorted(data.keys())]


def recursive_sort(data):
    """
    Recursive sort dict
    :param data: data to sort
    :type data: dict
    :return: sorted list
    :rtype: list
    """
    result = []
    for k, v in key_sort(data):
        if v is dict:
            v = key_sort(v)
        result.append((k, v))
    return result


def auth_sign(key, rn_data):
    """

    :param data:
    :return:
    """

    data = {}

    for k in set(rn_data):
        data[k] = rn_data.get(k)

    sign = data.pop("sign")

    data['secret'] = key

    digest_str = '&'.join('{0}={1}'.format(k, v) for (k, v) in recursive_sort(data))

    if hashlib.md5(digest_str).hexdigest() == sign:
        return True
    else:
        return False

