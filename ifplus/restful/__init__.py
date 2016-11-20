# -*- coding: utf-8 -*-
from .patched import Api


class Rest(object):
    def __init__(self, app=None, **kwargs):
        self.api = Api(title='IF+ Restful API',
                       version='1.0',
                       description='IF+ Restful API')
        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        setattr(app, 'api', self.api)
