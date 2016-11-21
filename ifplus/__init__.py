# -*- coding: utf-8 -*-
from flask.ext.pymongo import PyMongo
from .restful import Rest
from .res import VFS


class Application(object):
    def __init__(self, app=None, **kwargs):
        self.rest = None
        self.mongo = None
        self.auth = None
        self.res = None
        self.pm = None
        self.chat = None
        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        self.rest = Rest(app, **kwargs)
        self.mongo = PyMongo(app)
        setattr(app, 'mongo', self.mongo)
        self.res = VFS(app, **kwargs)

        self.rest.register()
