# -*- coding: utf-8 -*-
from .acls import FileAcls, M_WRITE

OWNER_HIT = 1
GROUP_HIT = 2
CONTRIBUTOR_HIT = 3
PUBLIC_HIT = 4


class FileHits(FileAcls):
    """文件点击工具类"""
    def __init__(self, underlying, vfs=None):
        super(FileHits, self).__init__(underlying, vfs=vfs)

    def init_hits(self):
        """初始化文件点击属性"""
        if u'hits' not in self.underlying:
            self.underlying[u'hits'] = {
                u'o': 0, u'g': 0, u'u': 0, u'p': 0,
            }
        return self

    @property
    def hits(self):
        """文件对象点击数"""
        return self.underlying[u'hits']

    def hit(self, user=None):
        if self.is_owner(user=user):
            self.changes[u'hits'] = OWNER_HIT
            return
        if self.is_group(user=user):
            self.changes[u'hits'] = GROUP_HIT
            return
        allow, deny, grant = self.perms(user=user)
        if allow & M_WRITE > 0:
            self.changes[u'hits'] = CONTRIBUTOR_HIT
        else:
            self.changes[u'hits'] = PUBLIC_HIT

    def get_hits(self, result=None):
        if result is None:
            result = {}
        result.update({
            u'hits': self.hits
        })
        return result

    def record_hits(self):
        self.result = self.get_hits(result=self.result)
        return self
