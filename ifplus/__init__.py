# -*- coding: utf-8 -*-
from flask_pymongo import PyMongo
from flask.ext.redis import FlaskRedis
from flask_cache import Cache
from .restful import Rest
from .rbac import RBAC
from .auth import Authenticator
from .vfs import VFS
from .chat import ChatServer


class Application(object):
    def __init__(self, app=None, **kwargs):
        self.rest = None
        self.mongo = None
        self.redis = None
        self.cache = None
        self.rbac = None
        self.auth = None
        self.vfs = None
        self.pm = None
        # self.chats = None
        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        self.rest = Rest(app=app, **kwargs)
        self.mongo = PyMongo(app=app)
        setattr(app, 'mongo', self.mongo)
        # self.redis = FlaskRedis(app=app)
        # setattr(app, 'redis', self.redis)
        self.cache = Cache(app, config=app.config['CACHE'])
        setattr(app, 'cache', self.cache)
        self.rbac = RBAC(app=app, **kwargs)
        self.auth = Authenticator(app=app, **kwargs)
        self.vfs = VFS(app=app,  mongo=self.mongo, **kwargs)
        # self.chats = ChatServer(app=app, **kwargs)
        self.rest.register()
        # print '注册 REST API'
        # self.chats.register()
        # print '注册 Socket-IO'

    def run(self, app, **kwargs):
        # self.chats.socketio.run(app, **kwargs)
        pass
