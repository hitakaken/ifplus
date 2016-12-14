# -*- coding: utf-8 -*-


class BaseFileNode(object):
    def __init__(self, underlying, vfs=None):
        # 底层存储文档
        self.underlying = underlying
        # 虚拟文件系统
        self.vfs = vfs
        # 输出结果
        self.result = {}
        # 变更列表
        self.changes = {
            u'inodes': set(),
            u'acl': False,
            u'hits': 0,
            u'content': set(),
            u'xattrs': set(),
        }

    @property
    def is_changed(self):
        return len(self.changes[u'inodes']) > 0 or self.changes[u'acl'] or self.changes[u'hits'] > 0 \
               or len(self.changes[u'content']) > 0 or len(self.changes[u'xattrs']) > 0
