# -*- coding: utf-8 -*-
# bitsAllSet
import os
import datetime
from bson import ObjectId
from errno import *
from .devices.base import RootDevice
from ..models.actions.indexes import MONGO_INDEXES
from ..models import comment
from ..models.exceptions import FuseOSError
from ..models.actions.rests import CREATE_OPS, READ_OPS, UPDATE_OPS, DELETE_OPS
from ..models.actions import content
from ..models.actions.acls import M_WRITE
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
        if u'ancestors' not in self.root_file.underlying:
            self.root_file.underlying[u'ancestors'] = []
        if u'parent' not in self.root_file.underlying:
            self.root_file.underlying[u'parent'] = None
        if u'mode' not in self.root_file.underlying:
            self.root_file.underlying[u'mode'] = 0x80000000 | 0o047750
        self.root_file.init_inode(u'', datetime.datetime.now()).init_acl().init_hits().init_xattrs()
        self.root_file.init_comments(False).init_tags()

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

    def lookup(self, fid):
        return self._lookup_by_id(fid)

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
            user = kwargs.get(u'user')
            if user is None or user.is_anonymous:
                raise FuseOSError(EPERM)
            file_path = u'home/' + unicode(user.account) + file_path[1:]
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

    def save(self, file_object):
        if file_object.is_newly:
            self.mongo.db.files.insert_one(file_object.underlying)
        else:
            pass

    def update_payload(self, file_object, payload, time=None, user=None, perms=None):
        if u'owner' in payload:
            file_object.uid = payload[u'owner']
        if u'group' in payload:
            file_object.gid = payload[u'group']
        if u'mode' in payload:
            mask = int(''.join([str(i) for i in sum(payload[u'mode'], [])]), 2)
            file_object.mode &= 0xFFFE00
            file_object.mode |= mask
        if u'acl' in payload:
            acl = []
            for ace in payload[u'acl']:
                permission = ace[u'perms']
                mask = int(''.join(
                    [str(permission[i][0]) for i in range(0, 8)] +
                    [str(permission[i][1]) for i in range(0, 8)] +
                    [str(permission[i][2]) for i in range(0, 8)]), 2)
                mask |= 0x80000000
                if ace[u'inherit'] == 1:
                    mask |= 0x81000000
                acl.append({u'sid': ace[u'sid'], u'mask': mask})
            if file_object.is_newly:
                acl_dict = {}
                for ace in acl:
                    acl_dict[ace[u'sid']] = ace
                new_aces = []
                added_aces = []
                for ace in file_object.acl:
                    if ace[u'sid'] in acl_dict:
                        new_aces.append(acl_dict[ace[u'sid']])
                        added_aces.append(ace[u'sid'])
                    else:
                        new_aces.append(ace)
                for ace in acl:
                    if ace[u'sid'] not in added_aces:
                        new_aces.append(ace)
                file_object.acl = new_aces
            else:
                file_object.update_acl(acl, user=user, perms=perms, ctime=time)
        if u'xattrs' in payload:
            file_object.update_xattrs(payload[u'xattrs'], user=user, perms=perms, ctime=time)
        if u'content' in payload and file_object.is_flie:
            file_object.storage_type = content.STORAGE_OBJECT
            file_object.content_type = content.CONTENT_TYPE_TEXT
            file_object.content = payload[u'content']
        if u'tags' in payload:
            file_object.add_tags(payload[u'tags'], user=user, perms=perms)
        return file_object

    def create(self, file_path, **kwargs):
        op = kwargs.get(u'op')
        if op not in CREATE_OPS:
            raise FuseOSError(EROFS)
        parts = self.resolve_file_path(file_path, **kwargs)
        if not isinstance(parts[-1], unicode):
            raise FuseOSError(EEXIST)
        user = kwargs.get(u'user')
        payload = kwargs.get(u'payload')
        now = datetime.datetime.now()
        # 创建文件夹
        if op == u'mkdir':
            # 检查待创建文件夹不存在
            if isinstance(parts[-2], unicode):
                raise FuseOSError(ENOENT)
            # 检查父文件对象已存在，并且是文件夹
            if isinstance(parts[-2], FileObject):
                parent = parts[-2]
            else:
                symlink, parent = parts[-2]
            if not parent.is_folder:
                raise FuseOSError(ENOTDIR)
            # 检查用户具有写权限
            allow, deny, grant = parent.user_perms(user=user)
            if allow & M_WRITE == 0:
                raise FuseOSError(EPERM)
            name = parts[-1]
            current_path = parent.file_path + name if parent.file_path[-1] == u'/' else parent.file_path + u'/' + name
            file_object = FileObject(current_path, {u'_id': ObjectId()}, vfs=self)
            file_object.is_newly = True
            file_object.init_inode(name, now, user=user).init_acl(parent.inherits).init_xattrs()
            file_object.init_comments(False).init_tags()
            file_object.init_tree(
                parent=parent.file_id,
                ancestors=[] if parent.file_id is None else parent.ancestors + [parent.name])
            file_object.mode = parent.mode
            file_object = self.update_payload(file_object, payload, time=now, user=user, perms=(0xFF, 0x00, 0xFF))
            self.save(file_object)
            self.returns(file_object)
            return 200
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
        user = kwargs.get(u'user')
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
        user = kwargs.get(u'user')
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
        if op not in DELETE_OPS:
            raise FuseOSError(EROFS)
        user = kwargs.get(u'user')
        parts = self.resolve_file_path(file_path, **kwargs)
        if op == u'mkdir':
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
