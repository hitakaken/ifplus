# -*- coding: utf-8 -*-
from ifplus.res.models.file import FileObject


class ChatRoom(FileObject):
    def __init__(self, room_path, **kwargs):
        super(ChatRoom, self).__init__(room_path, **kwargs)

    @classmethod
    def model(cls, ns, *args, **kwargs):
        return ns.model("ChatRoom", {

        })



