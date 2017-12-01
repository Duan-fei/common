# -*- coding:utf-8 -*-


from daisy.views.base import BaseView
from finance.decorators import require_login, permission_required, api_auth


class BaseFrontView(BaseView):
    auth_page = 'site.AuthView:login'
    decorators = [require_login]
    pass


class BaseAdminView(BaseView):
    pass

class BaseApiView(BaseView):
    decorators = [api_auth]

