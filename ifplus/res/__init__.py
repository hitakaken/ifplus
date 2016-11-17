# -*- coding: utf-8 -*-


class VFS(object):
    def __init__(self, app=None, **kwargs):
        if app is not None:
            self.app = app
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        pass
