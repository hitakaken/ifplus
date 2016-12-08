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

    @abstractmethod
    def access(self, path, mode, **kwargs):
        return 0

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

    @abstractmethod
    def getfacl(self, path, **kwargs):
        raise FuseOSError(EOPNOTSUPP)

    @abstractmethod
    def setfacl(self, path, aces, **kwargs):
        raise FuseOSError(EOPNOTSUPP)

    @classmethod
    def requests(cls, ns):
        """Restful请求解析器"""
        # Access Request Parser
        access_parser = ns.parser()
        access_parser.add_argument('mod', location='args', required=True, help="指定权限掩码")
        # Chmod Request Parser
        chmod_parser = access_parser.copy()
        chmod_parser.add_argument('rcs', location='args', help="是否递归")
        # Chown Request Parser
        chown_parser = ns.parser()
        chown_parser.add_argument('own', location='args', help='指定所有者')
        chown_parser.add_argument('grp', location='args', help='指定所有组')
        # Mkdir Request Parser
        mkdir_parser = chown_parser.copy()
        mkdir_parser.add_argument('mod', location='args', help='指定权限掩码')
        mkdir_parser.add_argument('fce', type=bool, location='args', help='是否创建父节点')
        # Rename Request Parser
        rename_parser = ns.parser()
        rename_parser.add_argument('tgt', location='args', required=True, help='目标文件名')
        rename_parser.add_argument('fce', type=bool, location='args', help='是否创建父节点')
        # Recursive Request Parser
        recursive_parser = ns.parser()
        recursive_parser.add_argument('rcs', location='args', help="是否递归")
        # Upload Request Parser
        upload_parser = mkdir_parser.copy()
        upload_parser.add_argument('file', location='files', type=FileStorage, required=True, help='上传文件')
        upload_parser.add_argument('ovw', type=bool, location='args', help='是否覆盖')
        # Xattrs Request Parser
        xattrs_parser = ns.parser()
        xattrs_parser.add_argument('xattrs.name', location='args', required=True, action='append', help='扩展属性名')
        xattrs_parser.add_argument('xattrs.value', location='args', action='append', help='扩展属性值')
        xattrs_parser.add_argument('flag', location='args', help='扩展属性设置标志')
        # ACL Request Parser
        acl_parser = ns.parser()
        acl_parser.add_argument('ace', location='args', required=True, action='append',
                                help='ACL条目，格式：[u|g|r]:<UUID>:[FFFFFFFF]')
        acl_parser.add_argument('rcs', type=bool, location='args', help='是否递归')
        return {
            'access': access_parser,
            'chmod': chmod_parser,
            'chown': chown_parser,
            'mkdir': mkdir_parser,
            'rename': rename_parser,
            'recursive': recursive_parser,
            'upload': upload_parser,
            'xattrs': xattrs_parser,
            'acl': acl_parser,
        }

    @classmethod
    def fs_action_response_model(cls, ns):
        return ns.model('FsActionResponse', {
            'status': fields.Integer(description='状态'),
            'msg': fields.String(desctipion='消息')
        })
