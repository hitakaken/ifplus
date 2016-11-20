# -*- coding: utf-8 -*-
from .helpers.files import VirtualFileSystem
from .views.vfs import ns


class VFS(object):
    def __init__(self, app=None, **kwargs):
        self.fs = None
        if app is not None:
            self.app = app
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        self.fs = VirtualFileSystem(None, None)
        setattr(app, 'fs', self.fs)
        app.api.add_namespace(ns)


