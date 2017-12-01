# -*- coding:utf-8 -*-
from datetime import datetime
from daisy.models.base import BaseModel
from daisy.contrib.sessions.models import BaseSessionStore
from bson import ObjectId
import time


class Session(BaseSessionStore):
    __collection__ = 'sessions'
    use_seq_id = 'session'
    structure = {
        '_id': ObjectId,
        'created_at': datetime,
        'updated_at': datetime,
        'expires': int,
        'name': basestring,
        'user_id': int,
    }
    default_values = {
        'created_at': datetime.utcnow,
        'updated_at': datetime.utcnow,
        'expires': int('%.0f' % time.time()) + 3600,
        '_id': ObjectId
    }

class DataStore(BaseModel):
    """
    Cache/Data store
    """
    __collection__ = 'data_store'
    structure = {
        '_id': basestring,
        'data': None,
    }

    def get_data(self, key):
        result = self.get_from_id(key)
        if result:
            return result.get('data')
        return None

    def set_data(self, key, data):
        self.update_doc({'_id': key}, {'$set': {'data': data}}, upsert=True)


class SysTaskQueue(BaseModel):
    """
    用于支持轻量的异步任务处理

    警告: 不可用于高负载的场景, 应使用真正的消息队列实现！
    """
    __collection__ = 'task_queues'
    structure = {
        'state': int,
        'type': basestring,
        'data': dict,
        'created_at': datetime,
    }
    default_values = {
        'created_at': datetime.utcnow,
        'state': 0,
    }


class SysNotification(BaseModel):
    """
    系统通知消息
    """
    __collection__ = 'sys_notifications'
    structure = {
        # 系统消息模板ID
        'notify_type_id': int,
        # 通知内容
        'data': dict,
        'created_at': datetime,
    }
    default_values = {
        'created_at': datetime.utcnow,
    }


class SysRuntimeCfg(BaseModel):
    """
    系统运行配置
    """
    __collection__ = "sys_runtime_cfg"
    structure = {
        '_id': basestring,
        'val': dict,
    }

    def save_val(self, k, val):
        spec = {'_id': k}
        doc = {'val': val}
        return self.update_set(spec, doc, upsert=True)

    def get_val(self, k):
        result = self.get_from_id(k)
        return result.get('val') if result else None
