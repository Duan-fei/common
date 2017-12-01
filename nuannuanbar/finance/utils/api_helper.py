# -*- coding:utf-8 -*-
import falcon
import json
import msgpack
import hmac
import hashlib
import urllib
from daisy.utils import convert
# from starship.rpc.protocol import ObjectSetResult

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict

from bson.json_util import (default as bson_object_default,
                            object_hook as bson_object_hook)

XML_TYPES = ('text/xml', 'application/xml')
JSON_TYPES = ('application/json', 'application/aes+json', 'application/x-www-form-urlencoded')
MSGPACK_TYPES = ('application/x-msgpack', 'application/msgpack',
                 'application/aes+msgpack')
AES_ENCODED = ('application/aes+json', 'application/aes+msgpack')


def api_error_serializer(req, resp, ex):
    """serializer to encode HttpError. It fallback serialize to json representation

    :param req:
    :type req:
    :param resp:
    :type resp:
    :param ex:
    :type ex:
    :return:
    :rtype:
    """
    preferred = req.content_type

    if preferred is None:
        accept = req.accept.lower()
        if '+json' in accept:
            preferred = 'application/json'
        elif '+msgpack' in accept:
            preferred = 'application/msgpack'
        else:
            preferred = 'application/json'
    if preferred is not None:
        resp.append_header('Vary', 'Accept')
        if preferred in JSON_TYPES:
            representation = json_dump(ex.to_dict())
        elif preferred in MSGPACK_TYPES:
            representation = msgpack_dump(ex.to_dict())
        elif preferred == 'application/xml':
            representation = ex.to_xml()
        else:
            representation = json_dump(ex.to_dict())

        resp.body = representation
        resp.content_type = preferred + '; charset=UTF-8'


class ApiExceptionHandler(object):
    @staticmethod
    def handle(ex, req, resp, params):
        req.context['error'] = ex


def handle_api_error(ex, req, resp, params):
    req.context['error'] = ex


_msgpack_packer = msgpack.Packer(default=bson_object_default, use_bin_type=True)


def json_load(s):
    s = urllib.unquote(s)
    return json.loads(s, encoding='utf-8', object_hook=bson_object_hook)


def json_dump(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, default=bson_object_default,
                      encoding='utf-8')


def msgpack_load(blob):
    return msgpack.unpackb(blob, encoding='utf-8', object_hook=bson_object_hook, use_list=True)


def msgpack_dump(obj):
    return _msgpack_packer.pack(obj)


def get_content_decoder(req):
    ct = get_content_type(req)
    if ct in JSON_TYPES:
        return json_load
    if ct in MSGPACK_TYPES:
        return msgpack_load
    return


def get_content_encoder(req):
    ct = req.content_type
    if ct in JSON_TYPES:
        return json_dump
    if ct in MSGPACK_TYPES:
        return msgpack_dump
    if ct in XML_TYPES:
        return
    return json_dump


def encode_ex(req, resp, ex, result_encoder=None):
    if result_encoder is None:
        result_encoder = get_content_encoder(req)
    if result_encoder:
        o = ex.to_dict()
        result = result_encoder(o)
        resp.status = falcon.HTTP_BAD_REQUEST
        resp.body = result


def encode_result(req, resp, result):
    result_encoder = get_content_encoder(req)
    if result_encoder:
        result = result_encoder(result)
    resp.body = result


def compute_x_auth_sign(sign_key, msg_id, ttl):
    return hmac.new(str(sign_key), '{0}:{1}'.format(msg_id, ttl), hashlib.md5).hexdigest()


def compute_x_token_sign(sign_key, access_token, msg_id, ttl):
    return hmac.new(str(sign_key), '{0}:{1}:{2}'.format(access_token, msg_id, ttl), hashlib.md5).hexdigest()


def get_content_type(req):
    """strip charset

    :param req:
    :type req:
    :return:
    :rtype:
    """
    ct = req.content_type
    if not ct:
        return
    w = ct.split(';')[0]
    return w.strip()


def safe_json_load(s):
    """Load json string, ignore value error

    :param s:
    :type s:
    :return:
    :rtype:
    """
    if not s:
        return
    try:
        return json_load(s)
    except ValueError:
        return


def process_query_meta(req):
    """Parse query meta in request query params

    :param req:
    :type req: falcon.request
    :return:
    :rtype:
    """
    # process params
    meta = {
        'where': None,
        'page': 1,
        'limit': 50,
        'sort': None,
    }
    if req.get_param('_meta'):
        _meta_json = safe_json_load(req.get_param('_meta'))
        meta.update(_meta_json)
    else:
        _where = safe_json_load(req.get_param('where'))
        if _where:
            meta['where'] = _where
        _page = convert.to_int(req.get_param('page'), 0)
        if _page:
            meta['page'] = _page
        _limit = convert.to_int(req.get_param('limit'), 0)
        if _limit:
            meta['limit'] = _limit
        _sort = safe_json_load(req.get_param('sort'))
        if _sort:
            meta['sort'] = _sort
    req.context['_meta'] = meta
    return meta


def ensure_find_safe_options(meta, max_limit=1000, **kwargs):
    """make find option more safe when invoke rpc

    :param meta:
    :type meta:
    :param max_limit:
    :type max_limit:
    :return:
    :rtype:
    """
    _limit = meta.get('_limit', 0)
    if _limit < 1 or _limit > max_limit:
        meta['_limit'] = 50
    _sort = meta.get('_sort', None)
    if not _sort:
        meta.pop('_sort')
    return meta


def query_meta_to_rpc_spec(meta, max_limit=1000, **kwargs):
    """ mapping query/find option to rpc find option params

    :param meta:
    :type meta:
    :param max_limit:
    :type max_limit:
    :param kwargs:
    :type kwargs:
    :return:
    :rtype:
    """
    options = {}
    if not meta:
        return ensure_find_safe_options(options, max_limit=max_limit)
    options['_limit'] = meta.get('limit', 0)
    options['_page'] = meta.get('page', 1)
    options['_sort'] = meta.get('sort', None)
    if meta.get('where'):
        options['_spec'] = meta.get('where')
    return ensure_find_safe_options(options)


def execute_object_set_result(results, page, limit):
    result_count = results.result_count
    results.has_more = False
    if result_count > page * limit:
        results.has_more = True
    return results


def find_all(client, method="find", spec=None, data_list=None, page=1, limit=30):
    if not data_list:
        data_list = []
    where = {
        "_page": page,
        "_limit": limit,
        "_spec": spec
    }
    result = getattr(client, method)(**where)
    result = execute_object_set_result(result, page, limit)
    for _result in result:
        if _result:
            data_list.append(_result)
    if result.has_more is True:
        return find_all(client, method, spec, data_list, page + 1, limit)
    return data_list
