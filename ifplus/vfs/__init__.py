# -*- coding: utf-8 -*-
from .helpers.vfs import VirtualFileSystem
from .views.files import ns


class VFS(object):
    def __init__(self, app=None, mongo=None, **kwargs):
        self.app = app
        self.mongo = mongo
        self.vfs = None
        if app is not None:
            self.app = app
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        self.app = app
        config = app.config.get('VFS', {})
        self.vfs = VirtualFileSystem(app,
                                     rid=config.get(u'RID', u'0000-0000-0000-0000'),
                                     root=config.get(u'ROOT', None),
                                     devices=config.get(u'DEVICES', None))
        setattr(self.app, 'vfs', self.vfs)
        self.app.api.add_namespace(ns)
