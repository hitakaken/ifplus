# -*- coding: utf-8 -*-
from flask import Blueprint
from .restful import Rest
from .res import VFS


class Application(object):
    def __init__(self, app=None, **kwargs):
        self.rest = None
        self.auth = None
        self.res = None
        self.pm = None
        self.chat = None
        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        self.rest = Rest(app, **kwargs)
        self.res = VFS(app, **kwargs)

        # 生成蓝图
        api_blueprint = Blueprint('api', __name__, url_prefix='/api')
        app.api.init_app(api_blueprint)
        app.register_blueprint(api_blueprint, **kwargs)
