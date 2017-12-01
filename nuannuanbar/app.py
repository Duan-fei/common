# -*- coding:utf-8 -*-
import os

from flask_cors import *
from finance import app
os.environ.setdefault('FINANCE_CFG', 'deploy/site.py')

app.bootstrap_dev_mode()
CORS(app)

if __name__ == '__main__':
    host = app.config.get('DEFAULT_HOST') or '0.0.0.0'
    port = app.config.get('DEFAULT_PORT') or 5010
    app.run(host='0.0.0.0', port=8022, debug=True)
