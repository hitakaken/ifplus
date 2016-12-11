# -*- coding: utf-8 -*-
from pymongo import IndexModel, ASCENDING, DESCENDING

MONGO_INDEXES = [
    IndexModel([(u'mtime', DESCENDING)], name=u'last_modify'),
    IndexModel([(u'uid', ASCENDING), (u'mtime', DESCENDING)], name=u'last_modify_by_user'),
    IndexModel([(u'ctime', DESCENDING)], name=u'last_change'),
    IndexModel([(u'uid', ASCENDING), (u'ctime', DESCENDING)], name=u'last_change_by_user'),
    IndexModel([(u'ctime', DESCENDING), (u'mtime', DESCENDING)], name=u'time_stamp'),
    IndexModel([(u'ancestors', ASCENDING), (u'name', ASCENDING)], name=u'path'),
    IndexModel([(u'parent', ASCENDING), (u'name', ASCENDING)], name=u'parent_and_name'),
]
