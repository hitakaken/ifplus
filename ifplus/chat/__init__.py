# -*- coding: utf-8 -*-
from flask_socketio import SocketIO

socketio = SocketIO()


class ChatServer(object):
    def __init__(self, app=None, **kwargs):
        self.app = app
        self.socketio = None
        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        self.app = app
        self.socketio = socketio
        setattr(app, 'socketio', self.socketio)

    def register(self):
        self.socketio.init_app(self.app)
