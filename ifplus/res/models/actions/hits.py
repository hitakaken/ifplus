# -*- coding: utf-8 -*-
from .acls import FileAcls


class FileHits(FileAcls):
    """文件点击工具类"""
    def __init__(self, underlying, vfs=None):
        super(FileHits, self).__init__(underlying, vfs=vfs)

