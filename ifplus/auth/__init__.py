# -*- coding: utf-8 -*-
from flask_login import LoginManager
from .views.tokens import ns
from .helpers.tokens import TokenHelper


class Auth(object):
    def __init__(self, app=None, **kwargs):
        self.app = app
        self.tokens = None
        self.login_manager = None
        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        self.app = app
        # LDAP 定义
        self.tokens = TokenHelper(jwt_config=app.config.get('JWT', {}), token_config=app.config.get('TOKEN', {}))
        self.login_manager = LoginManager(app=app)
        self.login_manager.request_loader(self.tokens.load_user_from_request)
        app.api.add_namespace(ns)
        setattr(app, 'tokens', self.tokens)
