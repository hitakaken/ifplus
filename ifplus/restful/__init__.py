# -*- coding: utf-8 -*-
from .patched import Api
from flask import Blueprint
from datatypes import ns


class Rest(object):
    def __init__(self, app=None, **kwargs):
        self.api = Api(title='IF+ Restful API',
                       version='1.0',
                       description='IF+ Restful API')
        self.api.add_namespace(ns)
        self.app = None
        self.url_prefix = None
        self.kwargs = {}
        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        setattr(app, 'api', self.api)
        self.app = app
        self.url_prefix = kwargs.get('url_prefix', '/api')
        self.kwargs = kwargs

    def register(self):
        # 生成蓝图
        api_blueprint = Blueprint('api', __name__, url_prefix=self.url_prefix)
        self.app.api.init_app(api_blueprint)
        self.app.register_blueprint(api_blueprint, **self.kwargs)
