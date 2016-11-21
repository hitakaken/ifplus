# -*- coding: utf-8 -*-
from flask_pymongo import PyMongo
from .restful import Rest
from .rbac import RBAC
from .res import VFS
from .chat import ChatServer


class Application(object):
    def __init__(self, app=None, **kwargs):
        self.rest = None
        self.mongo = None
        self.rbac = None
        self.auth = None
        self.res = None
        self.pm = None
        self.chats = None
        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        self.rest = Rest(app, **kwargs)
        self.mongo = PyMongo(app)
        setattr(app, 'mongo', self.mongo)
        self.rbac = RBAC(app=app, **kwargs)
        self.res = VFS(app=app,  mongo=self.mongo, **kwargs)
        self.chats = ChatServer(app=app, **kwargs)

        self.rest.register()
        self.chats.register()
