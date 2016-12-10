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
        # 是否新建文件对象
        self.newly = underlying is None
