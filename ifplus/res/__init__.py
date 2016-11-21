# -*- coding: utf-8 -*-
from .helpers.files import VirtualFileSystem
from .views.vfs import ns


class VFS(object):
    def __init__(self, app=None, **kwargs):
        self.fs = None
        self.app = None
        if app is not None:
            self.app = app
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        self.app = app
        self.fs = VirtualFileSystem(app.mongo.db.files, app.mongo.db.devices)
        setattr(self.app, 'fs', self.fs)
        self.app.api.add_namespace(ns)


