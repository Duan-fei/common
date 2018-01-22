# -*- coding: utf-8 -*-
import pymysql


def init_account():
    user = 'spider'
    host = 'rds93vu04hr3rn0o2d5io.mysql.rds.aliyuncs.com'
    db = 'spider'
    port = 3306
    passwd = 'abcde123!@#'
    conn = pymysql.connect(user=user, host=host, db=db, port=port, passwd=passwd)
    cur = conn.cursor()
    cur.execute("insert into account_info (id, username, status, email, password_hash, company_name) values (1, 'aiyunxia', 100, '15776572158@163.com','yuanding','yuanding1')")
    conn.commit()

if __name__ == '__main__':
   print init_account()
