# -*- coding: utf-8 -*-
# https://docs.mongodb.com/ecosystem/use-cases/storing-comments/
import datetime
import random
import string
from bson import ObjectId
from pymongo import IndexModel, ASCENDING, DESCENDING


def comment(fid, text, parent_slug=None, user=None, ts=None):
    if ts is None:
        ts = datetime.datetime.now()
    slug_part = u''.join(
        [unicode((string.ascii_letters + string.digits)[x], 'utf-8') for x in random.sample(range(0, 62), 4)])
    slug = parent_slug + u'/' + slug_part if parent_slug else slug
    return {
        u'_id': ObjectId(),
        u'fid': fid,
        u'user': {
            u'sid': user.sid,
            u'name': user.name,
            u'avator': user.avator
        },
        u'text': text,
        u'slug': slug,
        u'ts': ts
    }

MONGO_INDEXES = [
    IndexModel([(u'fid', ASCENDING), (u'slug', ASCENDING)], name=u'by_slug'),
    IndexModel([(u'fid', ASCENDING), (u'ts', DESCENDING)], name=u'by_timestamp'),
]