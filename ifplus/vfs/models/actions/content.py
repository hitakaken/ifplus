# -*- coding: utf-8 -*-
from errno import EPERM
from ...base.operations import FuseOSError
from .acls import FileAcls, M_READ, M_WRITE

STORAGE_GRIDFS = 0
STORAGE_OBJECT = 1
STORAGE_LOCALFS = 2
STORAGE_DEVICE = 3
STORAGE_HTTPURL = 4
STORAGE_HDFS = 10
STORAGE_CEPH = 11
STORAGE_UNKNOWN = 99

CONTENT_TYPE_BINARY = 0
CONTENT_TYPE_OBJECT = 1
CONTENT_TYPE_TEXT = 2
CONTENT_TYPE_URL = 3
CONTENT_TYPE_UNKNOWN = 99


class FileContent(FileAcls):
    """文件内容工具类"""

    def __init__(self, underlying, vfs=None):
        super(FileContent, self).__init__(underlying, vfs=vfs)

    def init_content(self, storage, ctype, uri=None, secret=False):
        """初始化文件内容熟悉"""
        if u'content' not in self.underlying:
            self.underlying[u'content'] = {
                u'storage': storage,
                u'ctype': ctype,
                u'uri': uri,
                u'secret': secret
            }
        return self

    @property
    def storage_type(self):
        """文件内容存储方式"""
        return self.underlying.get(u'content', {}).get(u'storage', STORAGE_UNKNOWN)

    @storage_type.setter
    def storage_type(self, storage_type):
        """设置文件内容存储方式"""
        self.underlying[u'content'][u'storage'] = storage_type
        self.changes[u'content'].add(u'storage')

    @property
    def content_type(self):
        """文件内容类型"""
        return self.underlying.get(u'content', {}).get(u'ctype', CONTENT_TYPE_UNKNOWN)

    @content_type.setter
    def content_type(self, content_type):
        """设置文件内容类型"""
        self.underlying[u'content'][u'ctype'] = content_type
        self.changes[u'content'].add(u'ctype')

    @property
    def content_uri(self):
        """文件内容链接"""
        return self.underlying.get(u'content', {}).get(u'uri', None)

    @content_uri.setter
    def content_uri(self, content_uri):
        """设置文件内容链接"""
        self.underlying[u'content'][u'uri'] = content_uri
        self.changes[u'content'].add(u'uri')

    @property
    def is_secret(self):
        """文件内容是否保密，保密则无法通过文件系统接口获得"""
        return self.underlying.get(u'content', {}).get(u'secret', False)

    def make_secret(self, user=None, perms=None):
        """保密文件内容"""
        if self.is_full_controller(user=user, perms=perms):
            self.underlying[u'content'][u'secret'] = True
            self.changes[u'content'].add(u'secret')
        else:
            raise FuseOSError(EPERM)

    def make_overt(self, user=None, perms=None):
        """公开文件内容"""
        if self.is_full_controller(user=user, perms=perms):
            self.underlying[u'content'][u'secret'] = False
            self.changes[u'content'].add(u'secret')
        else:
            raise FuseOSError(EPERM)

    def stream(self, user=None, perms=None, atime=None):
        """返回文件内容读取流"""
        allow, deny, grant = self.user_perms(user=user, perms=perms)
        if allow & M_READ == 0:
            raise FuseOSError(EPERM)
        self.visited(atime=atime)
        return self.vfs.stream(self)

    def read(self, user=None, perms=None, atime=None):
        """返回文件内容"""
        allow, deny, grant = self.user_perms(user=user, perms=perms)
        if allow & M_READ == 0:
            raise FuseOSError(EPERM)
        self.visited(atime=atime)
        return self.vfs.read(self)

    def write(self, data, user=None, perms=None, mtime=None):
        allow, deny, grant = self.user_perms(user=user, perms=perms)
        if allow & M_WRITE == 0:
            raise FuseOSError(EPERM)
        self.modified(mtime=mtime)
        return

    def get_content(self, result=None, user=None, perms=None, atime=None):
        """获取文件内容"""
        if result is None:
            result = {}
        result.update({
            u'content': self.read(user=user, perms=perms, atime=atime)
        })
        return result

    def record_content(self, user=None, perms=None, atime=None):
        """记录文件内容到临时结果"""
        self.result = self.get_content(result=self.result, user=user, perms=perms, atime=atime)
        return self
