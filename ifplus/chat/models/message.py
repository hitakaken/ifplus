# -*- coding: utf-8 -*-
from pymongo import IndexModel, ASCENDING, DESCENDING


class Message(object):
    def __init__(self,
                 rid=None,
                 ts=None,
                 mid=None,
                 edited_at=None,
                 edited_by=None,
                 msg=None,
                 fid=None,
                 metions=None,
                 pinned=True,
                 spippeted=False,
                 location=None,
                 exp=None,
                 **kwargs):
        pass

    MONGO_INDEXES = [
        IndexModel([('room', ASCENDING), ('ts', DESCENDING)], name='messages_in_room'),
    ]

