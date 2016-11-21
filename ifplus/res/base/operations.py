# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from errno import *
from os import strerror
from stat import S_ISDIR
from werkzeug.datastructures import FileStorage

from ifplus.restful.patched import fields


class FuseOSError(OSError):
    """FUSE 异常"""
    def __init__(self, errno, http_status=500):
        super(FuseOSError, self).__init__(errno, strerror(errno))
        self.http_status = http_status

    @classmethod
    def model(cls, ns):
        return ns.model('Errno', {
            'errno': fields.Integer(description='错误码', required=True),
            'message': fields.String(description='错误信息')
        })


class Operations(object):
    __metaclass__ = ABCMeta

    def __call__(self, op, *args, **kwargs):
        if not hasattr(self, op):
            raise FuseOSError(EFAULT)
        return getattr(self, op)(*args, **kwargs)

    @classmethod
    def fs_action_response_model(cls, ns):
        return ns.model('FsActionResponse', {
            'status': fields.Integer(description='状态'),
            'msg': fields.String(desctipion='消息')
        })

    @abstractmethod
    def access(self, path, mode, **kwargs):
        return 0

    @classmethod
    def access_request_model(cls, ns):
        parser = ns.parser()
        parser.add_argument('mode', location='args')
        return parser

    @abstractmethod
    def chmod(self, path, mode, **kwargs):
        raise FuseOSError(EROFS)

    @abstractmethod
    def chown(self, path, uid, gid, **kwargs):
        raise FuseOSError(EROFS)

    @abstractmethod
    def create(self, path, mode, fi=None, **kwargs):
        raise FuseOSError(EROFS)

    @abstractmethod
    def destroy(self, path, **kwargs):
        pass

    @abstractmethod
    def flush(self, path, fh, **kwargs):
        return 0

    @abstractmethod
    def fsync(self, path, datasync, fh, **kwargs):
        return 0

    @abstractmethod
    def fsyncdir(self, path, datasync, fh, **kwargs):
        return 0

    @abstractmethod
    def getattr(self, path, fh=None, **kwargs):
        if path != '/':
            raise FuseOSError(ENOENT)
        return dict(mode=(S_ISDIR | 0o750), nlink=2)

    @abstractmethod
    def getxattr(self, path, name, position=0, **kwargs):
        raise FuseOSError(EOPNOTSUPP)

    @abstractmethod
    def link(self, target, source, **kwargs):
        raise FuseOSError(EROFS)

    @abstractmethod
    def listxattr(self, path, **kwargs):
        return []

    @abstractmethod
    def mkdir(self, path, mode, **kwargs):
        raise FuseOSError(EROFS)

    @classmethod
    def mkdir_request_model(cls, ns):
        parser = ns.parser()
        parser.add_argument('usr', location='args')
        parser.add_argument('grp', location='args')
        parser.add_argument('mod', location='args')
        parser.add_argument('fce', type=bool, location='args')
        return parser

    @abstractmethod
    def mknod(self, path, mode, dev, **kwargs):
        raise FuseOSError(EROFS)

    @abstractmethod
    def open(self, path, flags, **kwargs):
        return 0

    @abstractmethod
    def opendir(self, path, **kwargs):
        return 0

    @abstractmethod
    def read(self, path, size, offset, fh, **kwargs):
        return FuseOSError(EIO)

    @abstractmethod
    def readdir(self, path, fh, **kwargs):
        return ['.', '..']

    @abstractmethod
    def readlink(self, path, **kwargs):
        return FuseOSError(ENOENT)

    @abstractmethod
    def release(self, path, fh, **kwargs):
        return 0

    @abstractmethod
    def releasedir(self, path, fh, **kwargs):
        return 0

    @abstractmethod
    def removexattr(self, path, name, **kwargs):
        raise FuseOSError(EOPNOTSUPP)

    @abstractmethod
    def rename(self, old, new, **kwargs):
        raise FuseOSError(EROFS)

    @abstractmethod
    def rmdir(self, path, **kwargs):
        raise FuseOSError(EROFS)

    @abstractmethod
    def setxattr(self, path, name, value, options, position=0, **kwargs):
        raise FuseOSError(EOPNOTSUPP)

    @abstractmethod
    def statfs(self, path, **kwargs):
        return {}

    @abstractmethod
    def symlink(self, target, source, **kwargs):
        """creates a symlink `target -> source` (e.g. ln -s source target)"""
        raise FuseOSError(EROFS)

    @abstractmethod
    def truncate(self, path, length, fh=None, **kwargs):
        raise FuseOSError(EROFS)

    @abstractmethod
    def unlink(self, path, **kwargs):
        raise FuseOSError(EROFS)

    @abstractmethod
    def utimens(self, path, times=None, **kwargs):
        """Times is a (atime, mtime) tuple. If None use current time."""
        return 0

    @abstractmethod
    def write(self, path, data, offset, fh, **kwargs):
        raise FuseOSError(EROFS)

    @classmethod
    def upload_model(cls, ns):
        parser = ns.parser()
        parser.add_argument('file', location='files', type=FileStorage, required=True)

    @abstractmethod
    def getfacl(self, path, **kwargs):
        raise FuseOSError(EOPNOTSUPP)

    @abstractmethod
    def setfacl(self, path, ace, **kwargs):
        raise FuseOSError(EOPNOTSUPP)
