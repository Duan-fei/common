# -*- coding:utf-8 -*-
import logging
from daisy import Daisy
from daisy.app import create_app as _create_daisy_app
from daisy.sessions import MongoSessionInterface
from daisy.utils.randomutil import random_ticket
from .visitor import Visitor
from . import config, views

from finance import config


class FinanceApp(Daisy):
    mongo = None
    core_loaded = False
    visitor_class = Visitor
    session_interface = MongoSessionInterface()

    def bootstrap_core(self):
        if self.core_loaded:
            return
        self.load_models()
        self.load_jinjia_globals()

    # def init_log(self):
    #     pass

    def load_jinjia_globals(self):
        from daisy.globals import current_visitor
        # global assets path handle
        default_static_url = self.config.get('STATIC_DOMAIN', '') + '/static'
        css_domain = self.config.get('CSS_DOMAIN', default_static_url)
        js_domain = self.config.get('JS_DOMAIN', default_static_url)
        img_domain = self.config.get('IMG_DOMAIN', default_static_url)
        bundle_domain = self.config.get('BUNDLE_DOMAIN', default_static_url)
        static_url = self.config.get('STATIC_URL', default_static_url)
        assets_url = "%s/%s" % (css_domain, 'assets')

        bundle_vendor_js = "%s/bundle/vendor-%s.js" % (bundle_domain, self.config['ASSET_VENDOR_JS_BUILD_VERSION'])
        bundle_vendor_css = "%s/bundle/vendor-%s.css" % (bundle_domain, self.config['ASSET_VENDOR_CSS_BUILD_VERSION'])

        bundle_wechat_js = "%s/bundle/wechat-app-%s.js" % (bundle_domain, self.config['ASSET_WECHAT_JS_BUILD_VERSION'])
        bundle_wechat_css = "%s/bundle/wechat-app-%s.css" % (
            bundle_domain, self.config['ASSET_WECHAT_CSS_BUILD_VERSION'])

        context = {
            'visitor': current_visitor,
            'static_url': static_url,
            'assets_url': assets_url,
            'css_url': '%s/css' % css_domain,
            'js_url': '%s/js' % js_domain,
            'img_url': '%s/images' % img_domain,
            'use_bundle_js': self.config.get('USE_BUNDLE_JS', False),
            'asset_js_bundles': self.config.get('ASSET_JS_BUNDLES', {}),
            'use_bundle_css': self.config.get('USE_BUNDLE_CSS', False),
            'bundle_vendor_js': bundle_vendor_js,
            'bundle_vendor_css': bundle_vendor_css,
            'bundle_wechat_js': bundle_wechat_js,
            'bundle_wechat_css': bundle_wechat_css,
            'random_ticket': random_ticket(),
        }
        self.jinja_env.globals.update(context)

    def mount_web(self):
        self.load_config_blueprint('site', views.BaseView)
        # load filters
        from . import filters
    #
    def load_models(self):
        self.register_mongokit_models('finance.models')

    def bootstrap_dev_mode(self):
        self.bootstrap_core()
        self.mount_web()

    def bootstrap_shell_mode(self, mount_views=True):
        self.bootstrap_core()
        if mount_views:
            self.mount_web()
        if self.config.get('SHELL_HOST'):
            self.config['SERVER_NAME'] = self.config['SHELL_HOST']


def create_app(name, envvar='FINANCE_CFG', runtime_cfg_dict=None):
    """Factory approval application instance
    :param name: app_name
    :param envvar: config environment load path
    :param runtime_cfg_dict: runtime configuration dict
    :return: :rtype: ApprovalApp
    """
    return _create_daisy_app(name, config, envvar=envvar, runtime_cfg_dict=runtime_cfg_dict,
                             app_cls=FinanceApp, static_folder='../static', static_url_path='/static')
