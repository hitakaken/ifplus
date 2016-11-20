# -*- coding: utf-8 -*-
# bitsAllSet
from errno import *
from ..base.operations import Operations, FuseOSError
from ..models.file import *


class VirtualFileSystem(Operations):
    def __init__(self, files, devices):
        self.files = files  # MongoDB Collection: files
        self.devices = devices  # 设备列表

    def register(self, device):
        pass

    def file_node(self, file_path):
        """根据路径获取文件节点"""

        pass

    def load(self, file_path):
        pass

    def access(self, path, mode, **kwargs):
        return 0

    def chmod(self, path, mode, **kwargs):
        raise FuseOSError(EROFS)

    def chown(self, path, uid, gid, **kwargs):
        raise FuseOSError(EROFS)

    def create(self, path, mode, fi=None, **kwargs):
        raise FuseOSError(EROFS)

    def destroy(self, path, **kwargs):
        pass

    def flush(self, path, fh, **kwargs):
        return 0

    def fsync(self, path, datasync, fh, **kwargs):
        return 0

    def fsyncdir(self, path, datasync, fh, **kwargs):
        return 0

    def getattr(self, path, fh=None, **kwargs):
        if path != '/':
            raise FuseOSError(ENOENT)
        return dict()

    def getxattr(self, path, name, position=0, **kwargs):
        raise FuseOSError(EOPNOTSUPP)

    def link(self, target, source, **kwargs):
        raise FuseOSError(EROFS)

    def listxattr(self, path, **kwargs):
        return []

    def mkdir(self, path, mode, **kwargs):
        raise FuseOSError(EROFS)

    def mknod(self, path, mode, dev, **kwargs):
        raise FuseOSError(EROFS)

    def open(self, path, flags, **kwargs):
        return 0

    def opendir(self, path, **kwargs):
        return 0

    def read(self, path, size, offset, fh, **kwargs):
        return FuseOSError(EIO)

    def readdir(self, path, fh, **kwargs):
        return ['.', '..']

    def readlink(self, path, **kwargs):
        return FuseOSError(ENOENT)

    def release(self, path, fh, **kwargs):
        return 0

    def releasedir(self, path, fh, **kwargs):
        return 0

    def removexattr(self, path, name, **kwargs):
        raise FuseOSError(EOPNOTSUPP)

    def rename(self, old, new, **kwargs):
        raise FuseOSError(EROFS)

    def rmdir(self, path, **kwargs):
        raise FuseOSError(EROFS)

    def setxattr(self, path, name, value, options, position=0, **kwargs):
        raise FuseOSError(EOPNOTSUPP)

    def statfs(self, path, **kwargs):
        return {}

    def symlink(self, target, source, **kwargs):
        """creates a symlink `target -> source` (e.g. ln -s source target)"""
        raise FuseOSError(EROFS)

    def truncate(self, path, length, fh=None, **kwargs):
        raise FuseOSError(EROFS)

    def unlink(self, path, **kwargs):
        raise FuseOSError(EROFS)

    def utimens(self, path, times=None, **kwargs):
        """Times is a (atime, mtime) tuple. If None use current time."""
        return 0

    def write(self, path, data, offset, fh, **kwargs):
        raise FuseOSError(EROFS)

    def getfacl(self, path, **kwargs):
        raise FuseOSError(EOPNOTSUPP)

    def setfacl(self, path, ace, **kwargs):
        raise FuseOSError(EOPNOTSUPP)

