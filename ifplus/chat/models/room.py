# -*- coding: utf-8 -*-
from ifplus.res.models.file import FileObject


class ChatRoom(FileObject):
    def __init__(self, room_path, **kwargs):
        super(ChatRoom, self).__init__(room_path, **kwargs)
        self.props = None

    @property
    def is_private(self):
        return self.props[u'private']

