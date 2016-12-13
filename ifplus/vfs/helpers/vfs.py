# -*- coding: utf-8 -*-
# bitsAllSet
import os
from errno import *
from .devices.base import RootDevice
from ..models.actions.indexes import MONGO_INDEXES
from ..models import comment
from ..models.exceptions import FuseOSError
from ..models.actions.rests import CREATE_OPS, READ_OPS, UPDATE_OPS, DELETE_OPS
from ..models.file import FileObject
# from .devices import MongoDevice
from ifplus.data.helpers.mongo_utils import init_indexes


class VirtualFileSystem(object):
    def __init__(self, app, rid=None, root=None, devices=None, **kwargs):
        # super(VirtualFileSystem, self).__init__(**kwargs)
        self.mongo = app.mongo  # MongoDB Collection: files
        self.cache = app.cache
        self.devices = {u'/': RootDevice(rid, self)}
        if devices is not None:
            self.devices.update(devices)
        self.root_file = FileObject(u'/', root, vfs=self)
        self.init_root_file()

    def init_mongo(self):
        init_indexes(self.mongo.db, 'files', MONGO_INDEXES)
        init_indexes(self.mongo.db, 'comments', comment.MONGO_INDEXES)

    def init_root_file(self):
        if self.root_file.underlying is None:
            self.root_file.underlying = {}
        if u'_id' not in self.root_file.underlying:
            self.root_file.underlying[u'_id'] = None
        if u'dev' not in self.root_file.underlying:
            self.root_file.underlying[u'dev'] = self.devices[u'/'].id
        if u'name' not in self.root_file.underlying:
            self.root_file.underlying[u'name'] = u''
        if u'ancestors' not in self.root_file.underlying:
            self.root_file.underlying[u'ancestors'] = []
        if u'parent' not in self.root_file.underlying:
            self.root_file.underlying[u'parent'] = None
        if u'mode' not in self.root_file.underlying:
            self.root_file.underlying[u'mode'] = 0x80000000 | 0o177750
        if u'nlink' not in self.root_file.underlying:
            self.root_file.underlying[u'nlink'] = 1
        if u'size' not in self.root_file.underlying:
            self.root_file.underlying[u'size'] = 0
        self.root_file.init_acl().init_hits().init_tags().init_xattrs().init_comments()

    # def device_of(self, file_path):
    #     path = file_path
    #     while path != '/':
    #         folder = os.path.dirname(path)
    #         if folder in self.devices:
    #             return self.devices[folder]
    #     return self.devices['/']
    #
    # def device_path(self, file_path, device=None):
    #     device = device if device is not None else self.device_of(file_path)
    #     return os.path.relpath(file_path, device.root)

    def _lookup_by_id(self, fid, current_path=None):
        underlying = self.mongo.db.files.find_one({u'_id': fid})
        if underlying is None:
            return None
        file_object = FileObject(current_path, underlying, vfs=self)
        if not file_object.is_link:
            return file_object
        else:
            return file_object, self._lookup_by_link(file_object, current_path=current_path)

    def _lookup_by_link(self, symlink, current_path=None):
        if symlink.is_link:
            file_object = self._lookup_by_id(symlink.symlink[u'id'], current_path=current_path)
            if not file_object.is_link:
                return file_object
            else:
                return file_object, self._lookup_by_link(file_object, current_path=current_path)
        return None

    def _lookup_by_parent_and_name(self, parent, name, current_path=None):
        underlying = self.mongo.db.files.find_one({u'parent': parent.file_id, u'name': name})
        if underlying is None:
            return None
        file_object = FileObject(current_path, underlying, vfs=self)
        if not file_object.is_link:
            return file_object
        else:
            return file_object, self._lookup_by_link(file_object, current_path=current_path)

    def _lookup_by_file_path(self, file_path, current_path=None):
        partnames = filter(bool, file_path.split(u'/'))
        underlying = self.mongo.db.files.find_one({u'ancestors': partnames[:-1], u'name': partnames[-1]})
        if underlying is None:
            return None
        file_object = FileObject(current_path, underlying, vfs=self)
        if not file_object.is_link:
            return file_object
        else:
            return file_object, self._lookup_by_link(file_object, current_path=current_path)

    def resolve_file_path(self, file_path, **kwargs):
        if file_path.startswith(u'~/'):
            file_path = u'home/' + unicode(kwargs.get(u'user').account) + file_path[1:]
        if not file_path.startswith(u'/'):
            file_path = u'/' + file_path
        if file_path == u'/':
            return [self.root_file]
        partnames = filter(bool, file_path.split(u'/'))
        parts = [self.root_file]
        current_path = u''
        for name in partnames:
            current_path += u'/' + name
            if isinstance(parts[-1], tuple):
                symlink, parent = parts[-1]
            else:
                parent = parts[-1]
            if not isinstance(parent, FileObject):
                parts.append(name)
                continue
            result = self._lookup_by_parent_and_name(parent, name, current_path=current_path)
            if result is None:
                parts.append(name)
            elif isinstance(result, FileObject):
                parts.append(result)
            else:
                file_object, symlink = result
                if symlink is None:
                    symlink = name
                parts.append((file_object, symlink))
        return parts

    def create(self, file_path, **kwargs):
        op = kwargs.get(u'op')
        if op not in CREATE_OPS:
            raise FuseOSError(EROFS)
        parts = self.resolve_file_path(file_path, **kwargs)
        print parts
        if op == u'mkdir':
            pass
        elif op == u'mkdirs':
            pass
        elif op == u'mkdirp':
            pass
        elif op == u'touch':
            pass
        elif op == u'link':
            pass
        raise FuseOSError(EROFS)

    def read(self, file_path, **kwargs):
        op = kwargs.get(u'op')
        if op not in READ_OPS:
            raise FuseOSError(EROFS)
        parts = self.resolve_file_path(file_path, **kwargs)
        if op == u'mkdir':
            pass
        elif op == u'mkdir':
            pass
        elif op == u'mkdir':
            pass
        raise FuseOSError(EROFS)

    def update(self, file_path, **kwargs):
        op = kwargs.get(u'op')
        if op not in UPDATE_OPS:
            raise FuseOSError(EROFS)
        parts = self.resolve_file_path(file_path, **kwargs)
        if op == u'mkdir':
            pass
        elif op == u'mkdir':
            pass
        elif op == u'mkdir':
            pass
        elif op == u'mkdir':
            pass
        raise FuseOSError(EROFS)

    def delete(self, file_path, **kwargs):
        op = kwargs.get(u'op')
        parts = self.resolve_file_path(file_path, **kwargs)
        if op not in DELETE_OPS:
            raise FuseOSError(EROFS)
        elif op == u'mkdir':
            pass
        elif op == u'mkdir':
            pass
        raise FuseOSError(EROFS)

    def upload(self, file_path, **kwargs):
        parts = self.resolve_file_path(file_path, **kwargs)
        pass

    def lookup(self, file_path):
        pass

    def mkdir(self, file_path, **kwargs):
        pass
