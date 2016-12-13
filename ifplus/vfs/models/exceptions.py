# -*- coding: utf-8 -*-
from os import strerror


class FuseOSError(OSError):
    """FUSE 异常"""
    def __init__(self, errno, http_status=500):
        super(FuseOSError, self).__init__(errno, strerror(errno))
        self.http_status = http_status
