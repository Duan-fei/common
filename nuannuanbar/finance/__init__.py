# -*- coding:utf-8 -*-
__author__ = 'night'

from .app import create_app
from flask_login import LoginManager

app = create_app(__name__)

login_manage = LoginManager()
login_manage.init_app(app)



