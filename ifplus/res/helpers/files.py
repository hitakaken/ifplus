# -*- coding: utf-8 -*-
# bitsAllSet
import os
from errno import *
from ..base.operations import Operations, FuseOSError
from ..models.file import FileMetaInfo, FileTreeNode, FileObject
from .local.virtual import VirtualDevice
from .devices import MongoDevice


class VirtualFileSystem(MongoDevice):
    def __init__(self, mongo, devices=None, **kwargs):
        super(VirtualFileSystem, self).__init__(mongo, **kwargs)
        self.mongo = mongo  # MongoDB Collection: files
        self.fs = self
        if devices is None:
            devices = {
                '/': VirtualDevice(u'/', fs=self)
            }
        self.devices = devices

    def register(self, device):
        pass

    def start(self):
        collection_names = self.mongo.db.collection_names()
        if 'files' not in collection_names:
            self.mongo.db.create_collection('files')
        indexes = self.mongo.db.files.index_information()
        indexes_to_create = []
        for file_index in FileMetaInfo.MONGO_INDEXES + FileTreeNode.MONGO_INDEXES:
            if file_index.document['name'] not in indexes:
                indexes_to_create.append(file_index)
        if len(indexes_to_create) > 0:
            self.mongo.db.files.create_indexes(indexes_to_create)

    def device_of(self, file_path):
        path = file_path
        while path != '/':
            folder = os.path.dirname(path)
            if folder in self.devices:
                return self.devices[folder]
        return self.devices['/']

    def device_path(self, file_path, device=None):
        device = device if device is not None else self.device_of(file_path)
        return os.path.relpath(file_path, device.root)

    def file_object(self, file_path):
        """根据路径获取文件节点"""
        return FileObject(file_path, filesystem=self, device=self.device_of(file_path))

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

    def mknod(self, path, mode, dev, **kwargs):
        raise FuseOSError(EROFS)

    # def open(self, path, flags, **kwargs):
    #    return 0

    def opendir(self, path, **kwargs):
        return 0

    def read(self, path, size, offset, fh, **kwargs):
        return FuseOSError(EIO)

    # def read(self, path, size, offset, fh, **kwargs):
    #    return FuseOSError(EIO)

    # def readdir(self, path, fh, **kwargs):
    #    return ['.', '..']

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

    # def write(self, path, data, offset, fh, **kwargs):
    #     raise FuseOSError(EROFS)

    # def getfacl(self, path, **kwargs):
    #    raise FuseOSError(EOPNOTSUPP)

    # def setfacl(self, path, ace, **kwargs):
    #    raise FuseOSError(EOPNOTSUPP)

