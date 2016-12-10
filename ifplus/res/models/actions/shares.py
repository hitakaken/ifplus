# -*- coding: utf-8 -*-
from errno import EPERM
from ...base.operations import FuseOSError
from .acls import FileAcls


class FileShares(FileAcls):
    """文件共享工具类"""
    def __init__(self, underlying, vfs=None):
        super(FileShares, self).__init__(underlying, vfs=vfs)