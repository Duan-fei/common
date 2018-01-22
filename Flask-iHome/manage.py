#!/usr/bin/env python
# -*- coding:utf-8 -*-
#项目启动文件
from ihome import create_app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import *
from ihome import models
#应用程序实例，指定开发者模式
app = create_app("development")
CORS(app)
#创建数据库表
Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)
print 11
print 22
print 33

if __name__ == '__main__':
    print app.url_map
    manager.run()


