# -*- coding: utf-8 -*-
from ifplus.restful.patched import fields
from ifplus.res.models.file import FileObject


class ChatRoom(FileObject):
    """聊天室对象"""

    def __init__(self, room_path, **kwargs):
        super(ChatRoom, self).__init__(room_path, **kwargs)

    def owner(self):
        pass

    def users(self):
        pass

    @classmethod
    def model(cls, ns, *args, **kwargs):
        return ns.model("ChatRoom", {
            "cid": fields.String(title="聊天室ID"),
            "name": fields.String(title="聊天室名"),
            "path": fields.String(title="聊天室路径"),
            "owner": fields.String(title="聊天室所有者"),
            "users": fields.List(fields.String(), title="用户列表")
        })



