# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from errno import *
from os import strerror
from stat import S_ISDIR


class FuseOSError(OSError):
    """FUSE 异常"""
    def __init__(self, errno):
        super(FuseOSError, self).__init__(errno, strerror(errno))


class Operations(object):
    __metaclass__ = ABCMeta

    def __call__(self, op, *args, **kwargs):
        if not hasattr(self, op):
            raise FuseOSError(EFAULT)
        return getattr(self, op)(*args, **kwargs)

    @abstractmethod
    def access(self, path, mode):
        return 0

    @abstractmethod
    def chmod(self, path, mode):
        raise FuseOSError(EROFS)

    @abstractmethod
    def chown(self, path, uid, gid):
        raise FuseOSError(EROFS)

    @abstractmethod
    def create(self, path, mode, fi=None):
        raise FuseOSError(EROFS)

    @abstractmethod
    def destroy(self, path):
        pass

    @abstractmethod
    def flush(self, path, fh):
        return 0

    @abstractmethod
    def fsync(self, path, datasync, fh):
        return 0

    @abstractmethod
    def fsyncdir(self, path, datasync, fh):
        return 0

    @abstractmethod
    def getattr(self, path, fh=None):
        if path != '/':
            raise FuseOSError(ENOENT)
        return dict(mode=(S_ISDIR | 0o750), nlink=2)

    @abstractmethod
    def getxattr(self, path, name, position=0):
        raise FuseOSError(EOPNOTSUPP)

    @abstractmethod
    def link(self, target, source):
        raise FuseOSError(EROFS)

    @abstractmethod
    def listxattr(self, path):
        return []

    @abstractmethod
    def mkdir(self, path, mode):
        raise FuseOSError(EROFS)

    @abstractmethod
    def mknod(self, path, mode, dev):
        raise FuseOSError(EROFS)

    @abstractmethod
    def open(self, path, flags):
        return 0

    @abstractmethod
    def opendir(self, path):
        return 0

    @abstractmethod
    def read(self, path, size, offset, fh):
        return FuseOSError(EIO)

    @abstractmethod
    def readdir(self, path, fh):
        return ['.', '..']

    @abstractmethod
    def readlink(self, path):
        return FuseOSError(ENOENT)

    @abstractmethod
    def release(self, path, fh):
        return 0

    @abstractmethod
    def releasedir(self, path, fh):
        return 0

    @abstractmethod
    def removexattr(self, path, name):
        raise FuseOSError(EOPNOTSUPP)

    @abstractmethod
    def rename(self, old, new):
        raise FuseOSError(EROFS)

    @abstractmethod
    def rmdir(self, path):
        raise FuseOSError(EROFS)

    @abstractmethod
    def setxattr(self, path, name, value, options, position=0):
        raise FuseOSError(EOPNOTSUPP)

    @abstractmethod
    def statfs(self, path):
        return {}

    @abstractmethod
    def symlink(self, target, source):
        """creates a symlink `target -> source` (e.g. ln -s source target)"""
        raise FuseOSError(EROFS)

    @abstractmethod
    def truncate(self, path, length, fh=None):
        raise FuseOSError(EROFS)

    @abstractmethod
    def unlink(self, path):
        raise FuseOSError(EROFS)

    @abstractmethod
    def utimens(self, path, times=None):
        """Times is a (atime, mtime) tuple. If None use current time."""
        return 0

    @abstractmethod
    def write(self, path, data, offset, fh):
        raise FuseOSError(EROFS)
