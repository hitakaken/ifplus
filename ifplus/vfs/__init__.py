# -*- coding: utf-8 -*-
from .helpers.vfs import VirtualFileSystem
from .views.files import ns


class VFS(object):
    def __init__(self, app=None, mongo=None, **kwargs):
        self.app = app
        self.mongo = mongo
        self.fs = None
        if app is not None:
            self.app = app
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        self.app = app
        self.fs = VirtualFileSystem(self.mongo)
        setattr(self.app, 'fs', self.fs)
        self.app.api.add_namespace(ns)
        from .views.files import vfs_bp
        self.app.register_blueprint(vfs_bp, url_prefix='/raw')



