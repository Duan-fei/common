# -*- coding:utf-8 -*-

# HOST配置
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 5010

# MONGODB数据库配置
MONGOKIT_POOL_DEFAULT = 'finance_default'
MONGODB_URI = 'mongodb://127.0.0.1'
MONGODB_DATABASE = 'god-view'
# mongo db options
MONGODB_OPTIONS = {}
# 若使用ReplicaSet请使用以下参数
# MONGODB_OPTIONS = { 'replicaSet': 'approval_rs1' }

# Session配置
SECRET_KEY = 'uqwen123&%@sdfK(*12S@@9845jsUDNsdf'
SESSION_COOKIE_NAME = 'god-view_sid'

# Memcached Servers
MEMCACHED_SERVERS = ['127.0.0.1:11211']
CACHE_KEY_PREFIX = 'god:'

# BLUEPRINTS LOADER
BLUEPRINTS = {
    'wechat': {
        'root': 'finance.wechat',
        'init_options': {
            'template_folder': 'templates',
        },
    },
    'admin': {
        'root': 'finance.admin',
        'init_options': {
            'template_folder': 'templates',
        },
    },
    'site': {
        'root': 'finance.site',
        'init_options': {
            'template_folder': 'templates',
        },
    },
}

DEBUG = True

ASSET_VENDOR_JS_BUILD_VERSION = '20160401'
ASSET_VENDOR_CSS_BUILD_VERSION = '20160401'

ASSET_WECHAT_JS_BUILD_VERSION = '20160401'
ASSET_WECHAT_CSS_BUILD_VERSION = '20160401'

# 短信模板
SMS_TEMPLATE = u'你的验证码是: {}'

SIOO_SMS_AUTH_STR = '***'

INIT_PASSWD = "***"

# CODE_FLAG = True
CODE_FLAG = False
# True 时真实发送短信

# 阿里大于配置
AL_SECRET_KEY = ''
AL_APP_KEY = ''
AL_SMS_FREE_SIGN_NAME = ''
AL_SMS_TEMPLATE_CODE = ''

AOAO_ACC_KEY = ''
AOAO_SER_KEY = ''
AOAO_URL = 'https://seaguard-dev.o3cloud.cn/1.0/'
# AOAO_URL = 'https://seaguard-dev.o3cloud.cn/1.0/'

MEMCACHED_FLAG = 'dev'

ADMINISTRATOR = ['']


MSG_SECRET = '123456'
