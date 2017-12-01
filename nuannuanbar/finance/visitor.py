# -*- coding:utf-8 -*-
__author__ = 'zjw'

from bson import ObjectId
from flask import session
from daisy.visitor import BaseVisitor
from daisy.globals import db


class Visitor(BaseVisitor):
    user = None
    user_id = None

    def load(self):
        user_id = session.get('user_id')
        if not user_id:
            # print user_id,'user_id'
            return
        user = db.Account.get_from_id(int(user_id))
        if not user:
            del session['user_id']
            session['_clear_session'] = True
            self.is_guest = True
            return
        self.user = user
        self.is_guest = False
        self.is_robot = False
        self.is_null_visitor = False
