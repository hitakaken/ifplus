# -*- coding: utf-8 -*-
from .hits import FileHits


class FileXattrs(FileHits):
    """文件扩展属性工具类"""
    def __init__(self, underlying, vfs=None):
        super(FileXattrs, self).__init__(underlying, vfs=vfs)

    def init_xattrs(self):
        """初始化文件扩展属性"""
        if u'xattrs' not in self.underlying:
            self.underlying[u'xattrs'] = {
                u'user': {},
                u'system': {},
            }
        return self

    @property
    def xattrs(self):
        return self.underlying[u'xattrs']

    def get_xattrs(self, result=None):
        if result is None:
            result = {}
        return result

    def record_xattrs(self):
        self.result = self.get_xattrs(result=self.result)
        return self
