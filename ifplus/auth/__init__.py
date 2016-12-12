# -*- coding: utf-8 -*-
from flask_login import LoginManager
from .views.tokens import ns
from .helpers.tokens import Tokens


class Authenticator(object):
    def __init__(self, app=None, **kwargs):
        self.app = app
        self.tokens = None
        self.login_manager = None
        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        self.app = app
        # LDAP 定义
        self.tokens = Tokens(app)
        self.tokens.init_mongodb()
        self.login_manager = LoginManager(app=app)
        self.login_manager.request_loader(self.tokens.load_user_from_request)
        app.api.add_namespace(ns)
        setattr(app, 'tokens', self.tokens)
        setattr(app, 'authenticator', self)
