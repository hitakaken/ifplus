# -*- coding: utf-8 -*-
# bitsAllSet
import os
from errno import *
from ..base.operations import Operations, FuseOSError
from ..models.file import FileObject
# from .devices import MongoDevice


class VirtualFileSystem(object):
    def __init__(self, mongo, cache, devices=None, **kwargs):
        # super(VirtualFileSystem, self).__init__(**kwargs)
        self.mongo = mongo  # MongoDB Collection: files
        self.fs = self
        if devices is None:
            devices = {
                '/': MongoDevice(u'/', fs=self)
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

    def destroy(self):
        pass

    def lookup(self, fid, name, ctx):
        pass

    def _lookup(self, fid, name, ctx):
        pass

    def getattr(self, id_, ctx):
        pass

    def readlink(self, id_, ctx):
        pass

    def opendir(self, id_,  ctx):
        pass

    def readdir(self, id_,  off):
        pass

    def getxattr(self, id_, name, ctx):
        pass

    def listxattr(self, id_, ctx):
        pass

    def setxattr(self, id_, name, value, ctx):
        pass

    def removexattr(self, id_, name, ctx):
        pass

    def lock_tree(self, id0):
        pass

    def remove_tree(self, id_p0, name0):
        pass

    def copy_tree(self, src_id, target_id):
        pass

    def unlink(self, id_p, name, ctx):
        pass

    def rmdir(self, id_p, name, ctx):
        pass

    def _remove(self, id_p, name, id_, force=False):
        pass

    def symlink(self, id_p, name, target, ctx):
        pass

    def rename(self, id_p_old, name_old, id_p_new, name_new, ctx):
        pass

    def _add_name(self, name):
        pass

    def _del_name(self, name):
        pass

    def _rename(self, id_p_old, name_old, id_p_new, name_new):
        pass

    def _replace(self, id_p_old, name_old, id_p_new, name_new, id_old,id_new):
        pass

    def link(self, id_, new_id_p, new_name, ctx):
        pass

    def setattr(self, id_, attr, fields, fh, ctx):
        pass

    def mknod(self, id_p, name, mode, rdev, ctx):
        pass

    def mkdir(self, id_p, name, mode, ctx):
        pass

    def extstat(self):
        pass

    def statfs(self, ctx):
        pass

    def open(self, id_, flags, ctx):
        pass

    def access(self, id_, mode, ctx):
        pass

    def create(self, id_p, name, mode, flags, ctx):
        pass

    def _create(self, id_p, name, mode, ctx, rdev, size):
        pass

    def read(self, fh, offset, length):
        pass

    def write(self, fh, offset, buf):
        pass

    def _readwrite(self, id_, offset, arg, buf=None, length=None):
        pass

    def fsync(self, fh, datasync):
        pass

    def forget(self, forget_list):
        pass

    def fsyncdir(self, fh, datasync):
        pass

    def releasedir(self):
        pass

    def release(self):
        pass

    def flush(self):
        pass
