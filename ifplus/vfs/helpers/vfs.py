# -*- coding: utf-8 -*-
# bitsAllSet
import json

import dpath
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId
from errno import *
from .devices.base import RootDevice
from ..models.actions.indexes import MONGO_INDEXES
from ..models import comment
from ..models.exceptions import FuseOSError
from ..models.actions.rests import CREATE_OPS, READ_OPS, UPDATE_OPS, DELETE_OPS
from ..models.actions import content
from ..models.actions.acls import M_WRITE, M_DELETE
from ..models.file import FileObject
# from .devices import MongoDevice
from ifplus.data.helpers.mongo_utils import init_collection, init_indexes
from ifplus.data.helpers.time_utils import utcnow


def normalize_payload(payload):
    temp = {}
    print payload
    for (k, v) in payload.items():
        dpath.util.new(temp, k, v, separator='.')
    return temp


class VirtualFileSystem(object):
    def __init__(self, app, rid=None, root=None, devices=None, **kwargs):
        # super(VirtualFileSystem, self).__init__(**kwargs)
        self.app = app
        self.mongo = app.mongo  # MongoDB Collection: files
        self.cache = app.cache
        self.devices = {u'/': RootDevice(rid, vfs=self)}
        if devices is not None:
            self.devices.update(devices)
        self.root_file = FileObject(u'/', root, vfs=self)
        self.init_root_file()

    def init_mongodb(self):
        init_collection(self.mongo.db, 'contents')
        init_indexes(self.mongo.db, 'files', MONGO_INDEXES)
        init_indexes(self.mongo.db, 'comments', comment.MONGO_INDEXES)

    def init_root_file(self):
        if self.root_file.underlying is None:
            self.root_file.underlying = {}
        if u'_id' not in self.root_file.underlying:
            self.root_file.underlying[u'_id'] = None
        if u'dev' not in self.root_file.underlying:
            self.root_file.underlying[u'dev'] = self.devices[u'/'].id
        if u'uid' in self.root_file.underlying and self.root_file.underlying[u'uid'].startswith(u'[Role]'):
            self.root_file.underlying[u'uid'] = self.app.tokens.get_role(self.root_file.underlying[u'uid'], sid=True)
        if u'gid' in self.root_file.underlying and self.root_file.underlying[u'gid'].startswith(u'[Role]'):
            self.root_file.underlying[u'gid'] = self.app.tokens.get_role(self.root_file.underlying[u'gid'], sid=True)
        if u'ancestors' not in self.root_file.underlying:
            self.root_file.underlying[u'ancestors'] = []
        if u'parent' not in self.root_file.underlying:
            self.root_file.underlying[u'parent'] = None
        if u'mode' not in self.root_file.underlying:
            self.root_file.underlying[u'mode'] = 0x80000000 | 0o047750
        self.root_file.init_inode(u'', utcnow()).init_acl().init_hits().init_xattrs()
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

    def lookup(self, input):
        if isinstance(input, ObjectId):
            return self._lookup_by_id(input)
        elif isinstance(input, unicode):
            return self._lookup_by_file_path(input)
        raise FuseOSError(EINVAL)

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
            file_object = self._lookup_by_id(ObjectId(symlink.symlink[u'id']), current_path=current_path)
            if not file_object.is_link:
                return file_object
            else:
                return file_object, self._lookup_by_link(file_object, current_path=current_path)
        return None

    def _lookup_by_parent_and_name(self, parent, name, current_path=None):
        underlying = self.mongo.db.files.find_one({u'parent': parent.id, u'name': name})
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
        if file_path.startswith(u'~'):
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

    def get_device_of(self, file_object):
        partnames = file_object.partnames
        for i in range(0, len(partnames)):
            current_path = u'/' + u'/'.join(partnames[0:i])
            if current_path in self.devices:
                return self.devices[current_path]
        return self.devices[u'/']

    def save(self, file_object, **kwargs):
        device = self.get_device_of(file_object)
        device.save(file_object, **kwargs)

    def remove(self, file_object, **kwargs):
        device = self.get_device_of(file_object)
        device.remove(file_object, **kwargs)

    def write_stream(self, file_object, steam, **kwargs):
        device = self.get_device_of(file_object)
        device.write_stream(file_object, steam, **kwargs)

    def read_stream(self, file_object, **kwargs):
        device = self.get_device_of(file_object)
        return device.read_stream(file_object, **kwargs)

    def read_text(self, file_object, **kwargs):
        device = self.get_device_of(file_object)
        return device.read_text(file_object, **kwargs)

    @staticmethod
    def update_payload(file_object, payload, time=None, user=None, perms=None):
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
        if u'content' in payload and file_object.is_file:
            file_object.storage_type = content.STORAGE_OBJECT
            file_object.content_type = content.CONTENT_TYPE_TEXT
            file_object.content = payload[u'content']
            file_object.modified(mtime=time)
        if u'tags' in payload:
            file_object.update_tags(payload[u'tags'], user=user, perms=perms)
        if u'link' in payload:
            pass
        return file_object

    @staticmethod
    def returns(file_object, returns, display_path, user=None, perms=None, atime=None):
        xattrs_namespace = []
        xattrs_attrnames = []
        for key in returns:
            if key == u'path':
                file_object.record_real_path()
                if file_object.is_link:
                    file_object.record_symlink()
            elif key == u'inodes':
                file_object.record_inodes()
                file_object.record_perms(user=user)
                if file_object.is_link:
                    file_object.record_symlink()
            elif key == u'acl':
                file_object.record_perms(user=user)
                file_object.record_acl()
            elif key == u'hits':
                file_object.record_hits()
            elif key == u'tags':
                file_object.record_tags()
            elif key.startswith(u'xattrs.'):
                xattr = key[7:]
                if u'.' in xattr:
                    xattrs_attrnames.append(xattr)
                else:
                    xattrs_namespace.append(xattr)
            elif key == u'content':
                file_object.record_content(user=user, perms=perms, atime=atime)
        if len(xattrs_namespace) + len(xattrs_attrnames) > 1:
            file_object.record_xattrs(xattrs_namespace, xattrs_attrnames)
        file_object.result.update({u'display_path': display_path, u'name': file_object.name})
        return file_object.result

    @staticmethod
    def get_display_path(file_path):
        if file_path[0] == u'/':
            display_path = file_path
        else:
            display_path = u'/' + file_path
        if display_path[-1] == u'/':
            display_path = display_path[:-1]
        return display_path

    def create(self, file_path, **kwargs):
        display_path = self.get_display_path(file_path)
        op = kwargs.get(u'op')
        if op not in CREATE_OPS:
            raise FuseOSError(EROFS)
        parts = self.resolve_file_path(file_path, **kwargs)
        if not isinstance(parts[-1], unicode):
            raise FuseOSError(EEXIST)
        user = kwargs.get(u'user')
        payload = kwargs.get(u'payload') if kwargs.get(u'payload') is not None else {}
        if kwargs[u'edit'] is not None and kwargs[u'edit'] > 0:
            payload = normalize_payload(payload)
        returns = kwargs.get(u'returns') if kwargs[u'returns'] is not None else [u'path']
        now = utcnow()
        if op == u'mkdir' or op == u'mkdirs' or op == u'touch' or op == u'link':
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
            file_object.init(parent, name, time=now, user=user, is_file=(op == u'touch'))
            file_object = self.update_payload(file_object, payload, time=now, user=user, perms=(0xFF, 0x00, 0xFF))
            # 创建文件夹
            if op == u'mkdir':
                self.save(file_object, **kwargs)
                return self.returns(file_object, returns, display_path, user=user, perms=(0xFF, 0x00, 0xFF))
            # 创建文件夹及其子文件夹
            elif op == u'mkdirs':
                results = [self.returns(file_object, returns, display_path,
                                        user=user, perms=(0xFF, 0x00, 0xFF), atime=now)]
                files = [file_object]
                if kwargs[u'subdir'] is not None:
                    for subdirname in kwargs.get(u'subdir', []):
                        sub_object = FileObject(current_path + u'/' + subdirname, {u'_id': ObjectId()}, vfs=self)
                        sub_object.init(file_object, subdirname, time=now, user=user)
                        results.append(self.returns(sub_object, returns, display_path + u'/' + subdirname,
                                                  user=user, perms=(0xFF, 0x00, 0xFF), atime=now))
                        files.append(sub_object)
                    for f in files:
                        self.save(f, **kwargs)
                return {u'files': results}
            # 创建文件
            elif op == u'touch':
                file_object.underlying[u'mode'] &= 0x80000000 | 0o007777
                file_object.underlying[u'mode'] |= 0o100000
                self.save(file_object, **kwargs)
                return self.returns(file_object, returns, display_path, user=user, perms=(0xFF, 0x00, 0xFF), atime=now)
            elif op == u'link':
                if u'target' not in kwargs:
                    raise FuseOSError(EINVAL)
                target_parts = self.resolve_file_path(kwargs[u'target'], **kwargs)
                if isinstance(target_parts[-1], unicode):
                    raise FuseOSError(ENOENT)
                if isinstance(target_parts[-1], tuple):
                    raise FuseOSError(EMLINK)
                target_file = target_parts[-1] # self._lookup_by_file_path(kwargs.get(u'target'))
                if target_file is None:
                    raise FuseOSError(ENOENT)
                file_object.init_symlink(target_file)
                target_file.add_link(file_object)
                self.save(file_object, **kwargs)
                self.save(target_file, **kwargs)
                return self.returns(file_object, returns, display_path, user=user, perms=(0xFF, 0x00, 0xFF), atime=now)
        elif op == u'mkdirp':
            pass
        raise FuseOSError(EROFS)

    def read(self, file_path, **kwargs):
        display_path = self.get_display_path(file_path)
        op = kwargs.get(u'op')
        if op not in READ_OPS:
            raise FuseOSError(EROFS)
        user = kwargs.get(u'user')
        parts = self.resolve_file_path(file_path, **kwargs)
        now = utcnow()
        # 检查待读取对象是否存在
        if isinstance(parts[-1], unicode):
            raise FuseOSError(ENOENT)
        if isinstance(parts[-1], FileObject):
            file_object = parts[-1]
        else:
            symlink, file_object = parts[-1]
        # 获取用户权限
        allow, deny, grant = file_object.user_perms(user=user)
        returns = kwargs.get(u'returns') if kwargs[u'returns'] is not None else [u'path']
        ask_perms = 0x00
        for key in returns:
            if key == u'content':
                ask_perms |= 0x80
            elif key == u'acl':
                ask_perms |= 0x80
            elif key == u'comments':
                ask_perms |= 0x80
            elif key == u'tags':
                ask_perms |= 0x80
            elif key.startswith(u'xattrs.'):
                ask_perms |= 0x80
        if op == u'stat':
            if allow & ask_perms == 0 and ask_perms > 0:
                raise FuseOSError(EPERM)
            result = self.returns(file_object, returns, display_path, user=user, perms=(allow, deny, grant), atime=now)
            if file_object.is_changed:
                self.save(file_object, **kwargs)
            return result
        elif op == u'list':
            if not file_object.is_folder:
                raise FuseOSError(ENOTDIR)
            ask_perms |= 0x20
            query = {}
            if kwargs[u'query'] is not None:
                try:
                    query_dict = json.loads(kwargs[u'query'], encoding='utf-8')
                    for (k, v) in query_dict.items():
                        if not k.startswith(u'xattrs.'):
                            k = u'xattrs.'+ k
                        query[k] = v
                except TypeError, e:
                    raise FuseOSError(EINVAL)
            if kwargs[u'filter'] is not None:
                for filter in kwargs[u'filter']:
                    if filter == u'folder':
                        query.update({u'mode': {u'$bitsAllSet': 0o040000}})
                    if filter == u'file':
                        query.update({u'mode': {u'$bitsAllSet': 0o100000}})
                    if filter == u'link':
                        query.update({u'mode': {u'$bitsAllSet': 0o120000}})
            if allow & ask_perms == 0:
                raise FuseOSError(EPERM)
            # if u'inodes' not in returns:
            #     returns.append(u'inodes')
            if u'content' in returns:
                returns.remove(u'content')
            if u'recursion' in kwargs and kwargs[u'recursion'] > 0:
                if u'withlinks' in kwargs and kwargs[u'withlinks'] > 0:
                    raise FuseOSError(ENOSYS)
                for index, partname in enumerate(file_object.partnames):
                    query[u'ancestors.' + str(index)] = partname
                is_page = False
                if kwargs[u'drop'] is not None or kwargs[u'take'] is not None:
                    drop = 0 if kwargs[u'drop'] is None else kwargs[u'drop']
                    take = 10 if kwargs[u'take'] is None else kwargs[u'take']
                    if take > 500:
                        take = 500
                    file_documents = self.mongo.db.files.find(query).skip(drop).limit(take)
                    is_page = True
                    kwargs[u'selfmode'] = 1
                else:
                    file_documents = self.mongo.db.files.find(query)
                file_objects = [FileObject(None, file_document, vfs=self) for file_document in file_documents]
                file_objects = sorted(
                    file_objects,
                    key=lambda temp_obj: tuple(temp_obj.ancestors + [temp_obj.name]))
                for file_obj in file_objects:
                    file_obj.file_path = file_obj.real_path
                children = [self.returns(file_obj, returns, file_obj.file_path,
                                     user=user, atime=now)
                        for file_obj in file_objects]
                if kwargs[u'selfmode'] is not None and kwargs[u'selfmode'] > 0:
                    result = self.returns(file_object, returns, file_object.real_path,
                        user=user, perms=(allow, deny, grant), atime=now)
                    result[u'children'] = children
                else:
                    result = children
                if is_page:
                    result[u'count'] = file_documents.count()
                    result[u'page'] = page
                    result[u'size'] = size
                return result
            else:
                if u'inodes' not in returns:
                    returns.append(u'inodes')
                query.update({u'parent': file_object.id})
                file_documents = self.mongo.db.files.find(query).sort([(u'mode', 1), (u'name', 1)])
                current_path = file_object.real_path
                file_objects = [FileObject(current_path + u'/' + file_document[u'name'], file_document, vfs=self)
                                for file_document in file_documents]
                children = [self.returns(file_obj, returns, display_path + u'/' + file_obj.name,
                                     user=user, atime=now)
                        for file_obj in file_objects]
                if kwargs[u'selfmode'] is not None and kwargs[u'selfmode'] > 0:
                    result = self.returns(file_object, returns, display_path,
                        user=user, perms=(allow, deny, grant), atime=now)
                    result[u'children'] = children
                else:
                    result = children
                return result
        elif op == u'download':
            ask_perms |= 0x80
            if allow & ask_perms == 0:
                raise FuseOSError(EPERM)
            if not file_object.is_file:
                raise FuseOSError(EISDIR)
            file_object.hit(user=user, atime=now)
            return self.read_stream(file_object, **kwargs)
        raise FuseOSError(EROFS)

    def update(self, file_path, **kwargs):
        display_path = self.get_display_path(file_path)
        op = kwargs.get(u'op')
        if op not in UPDATE_OPS:
            raise FuseOSError(EROFS)
        parts = self.resolve_file_path(file_path, **kwargs)
        # 检查待读取对象是否存在
        if isinstance(parts[-1], unicode):
            raise FuseOSError(ENOENT)
        if isinstance(parts[-1], FileObject):
            file_object = parts[-1]
        else:
            symlink, file_object = parts[-1]
        returns = kwargs.get(u'returns') if kwargs[u'returns'] is not None else [u'path']
        user = kwargs.get(u'user')
        allow, deny, grant = file_object.user_perms(user=user)
        now = utcnow()
        if op == u'update':
            payload = kwargs.get(u'payload') if kwargs.get(u'payload') is not None else {}
            if kwargs[u'edit'] is not None and kwargs[u'edit'] > 0:
                payload = normalize_payload(payload)
            ask_perm = 0x00
            if u'owner' in payload:
                ask_perm |= 0xff
            if u'group' in payload:
                ask_perm |= 0xff
            if u'mode' in payload:
                ask_perm |= 0xff
            if u'acl' in payload:
                ask_perm |= 0x08
            if u'xattrs' in payload:
                ask_perm |= 0x04
            if u'content' in payload and file_object.is_file:
                ask_perm |= 0x40
                file_object.modified(mtime=now)
            if u'comments' in payload:
                ask_perm |= 0x02
            if u'tags' in payload:
                ask_perm |= 0x02
            if ask_perm & allow == 0:
                raise FuseOSError(EPERM)
            self.update_payload(file_object, payload, time=now, user=user, perms=(allow,deny,grant))
            self.save(file_object, **kwargs)
            return self.returns(file_object, returns, display_path, user=user, perms=(allow,deny,grant))
        elif op == u'rename':
            pass
        elif op == u'move':
            pass
        raise FuseOSError(EROFS)

    def delete(self, file_path, **kwargs):
        display_path = self.get_display_path(file_path)
        op = kwargs.get(u'op')
        if op not in DELETE_OPS:
            raise FuseOSError(EROFS)
        user = kwargs.get(u'user')
        parts = self.resolve_file_path(file_path, **kwargs)
        # 检查待读取对象是否存在
        if isinstance(parts[-1], unicode):
            raise FuseOSError(ENOENT)
        symlink = None
        if isinstance(parts[-2], FileObject):
            parent = parts[-2]
        else:
            parent_symlink, parent = parts[-2]
        if isinstance(parts[-1], FileObject):
            current = parts[-1]
        else:
            symlink, current = parts[-1]
        allow, deny, grant = parent.user_perms(user)
        if allow & M_WRITE == 0:
            raise FuseOSError(EPERM)
        allow, deny, grant = current.user_perms(user)
        if deny & M_DELETE > 0:
            raise FuseOSError(EPERM)
        if symlink is not None:
            op = u'unlink'
        if op == u'rmdir':
            return self.remove(current, **kwargs)
        elif op == u'rm':
            return self.remove(current, **kwargs)
        elif op == u'unlink':
            current.remove_link(symlink)
            self.save(current, **kwargs)
            return self.remove(symlink, **kwargs)
        raise FuseOSError(EROFS)

    def upload(self, file_path, **kwargs):
        parts = self.resolve_file_path(file_path, **kwargs)
        now = utcnow()
        user = kwargs.get(u'user')
        # 目标不存在
        if isinstance(parts[-1], unicode):
            name = parts[-1]
            # 父节点存在
            if isinstance(parts[-2], unicode):
                raise FuseOSError(ENOENT)
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
            current_path = parent.file_path + name if parent.file_path[-1] == u'/' else parent.file_path + u'/' + name
            file_object = FileObject(current_path, {u'_id': ObjectId()}, vfs=self)
            file_object.init(parent, name, time=now, user=user, is_file=True)
        else:
            if isinstance(parts[-1], FileObject):
                current = parts[-1]
            else:
                symlink, current = parts[-1]
            # 检查用户具有写权限
            allow, deny, grant = current.user_perms(user=user)
            if allow & M_WRITE == 0:
                raise FuseOSError(EPERM)
            if current.is_folder:
                name = kwargs.get(u'file').filename
                exists = self._lookup_by_parent_and_name(current, name)
                if exists is None:
                    current_path = current.file_path + name if current.file_path[-1] == u'/' \
                        else current.file_path + u'/' + name
                    file_object = FileObject(current_path, {u'_id': ObjectId()}, vfs=self)
                    file_object.init(current, name, time=now, user=user, is_file=True)
                else:
                    file_object = exists
            else:
                file_object = current
        self.write_stream(file_object, kwargs.get(u'file'), **kwargs)
        return file_object.record_inodes().record_hits().result

    def lookup_user(self, sid):
        return self.app.tokens.lookup_user(sid)
