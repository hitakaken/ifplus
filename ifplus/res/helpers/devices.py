# -*- coding: utf-8 -*-
import datetime
from bson import ObjectId
from errno import *
from stat import *

from ..base.operations import Operations, FuseOSError
from ..models.file import FileObject
from abc import ABCMeta


PLACEHOLDER = 0x80000000


class MongoDevice(Operations):
    __metaclass__ = ABCMeta

    def __init__(self, mongo, **kwargs):
        self.mongo = mongo
        self.root = kwargs['root'] if 'root' in kwargs else None

    def real_path(self, path):
        return path if self.root is None else path.join(self.root, path)

    def path_nodes(self, path):
        part_names = filter(bool, self.real_path(path).split('/'))
        nodes = []
        parent = None
        is_first = True
        for name in part_names:
            if not is_first and parent is None:
                nodes.append(name)
                continue
            is_first = False
            underlying = self.mongo.db.files.find_one({
                u'parent': None if parent is None else parent.underlying[u'_id'],
                u'name': name})
            if underlying is None:
                nodes.append(name)
                parent = None
                continue
            paths = underlying.get(u'ancestors', [])
            paths.append(underlying[u'name'])
            parent = FileObject(u'/' + u'/'.join(paths), underlying=underlying, filesystem=self.fs)
            # TODO 检查是否为软链接
            nodes.append(parent)
        return nodes

    @staticmethod
    def create_document(name, parent, mode=0o750, mask=S_IFDIR, **kwargs):
        now = datetime.datetime.now()
        return {
                u'_id': ObjectId(),
                u'name': name,
                u'parent': parent.underlying[u'_id'] if parent is not None else None,
                u'ancestors': parent.underlying[u'ancestors'] + [parent.underlying[u'name']]
                if parent is not None else [],
                u'uid': None,
                u'creator': None,
                u'gid': None if 'group' not in kwargs else kwargs.get('group'),
                u'create': now,
                u'atime': now,
                u'mtime': now,
                u'ctime': now,
                u'mode': PLACEHOLDER | (mask | mode),
                u'dev': parent.underlying[u'dev'] if parent is not None else None,
                u'acl': parent.acl().inherit_acl() if parent is not None else [],
                u'size': 0,
                u'nlink': 0,
                u'xattrs': {}
            }

    def create_node(self, document):
        return FileObject(u'/' + u'/'.join(document[u'ancestors'] + [document[u'name']]),
                          underlying=document, filesystem=self.fs)

    def access(self, path, mode, **kwargs):
        nodes = self.path_nodes(path)
        return 0

    def chmod(self, path, mode, **kwargs):
        nodes = self.path_nodes(path)
        raise FuseOSError(EROFS)

    def chown(self, path, uid, gid, **kwargs):
        nodes = self.path_nodes(path)
        raise FuseOSError(EROFS)

    def create(self, path, mode, fi=None, **kwargs):
        nodes = self.path_nodes(path)
        raise FuseOSError(EROFS)

    def destroy(self, path, **kwargs):
        nodes = self.path_nodes(path)
        pass

    def flush(self, path, fh, **kwargs):
        nodes = self.path_nodes(path)
        return 0

    def fsync(self, path, datasync, fh, **kwargs):
        nodes = self.path_nodes(path)
        return 0

    def fsyncdir(self, path, datasync, fh, **kwargs):
        nodes = self.path_nodes(path)
        return 0

    def getattr(self, path, fh=None, **kwargs):
        nodes = self.path_nodes(path)
        if path != '/':
            raise FuseOSError(ENOENT)
        return dict()

    def getxattr(self, path, name, position=0, **kwargs):
        nodes = self.path_nodes(path)
        raise FuseOSError(EOPNOTSUPP)

    def link(self, target, source, **kwargs):
        nodes = self.path_nodes(source)
        raise FuseOSError(EROFS)

    def listxattr(self, path, **kwargs):
        nodes = self.path_nodes(path)
        return []

    def mkdir(self, path, mode, **kwargs):
        nodes = self.path_nodes(path)
        if type(nodes[-1]) != unicode:
            raise FuseOSError(EEXIST, http_status=400)
        if len(nodes) > 1 and type(nodes[-2]) == unicode and ('force' not in kwargs or not kwargs['force']):
            raise FuseOSError(ENOENT, http_status=404)
        parent = None
        for node in nodes:
            if type(node) != unicode:
                # 检查是否为文件夹
                if not S_ISDIR(node.underlying.get(u'mode')):
                    raise FuseOSError(ENOTDIR, http_status=400)
                parent = node
                continue
            # TODO 检查权限
            folder_document = self.create_document(node, parent, mode, mask=S_IFDIR, **kwargs)
            self.mongo.db.files.insert(folder_document)
            parent = self.create_node(folder_document)
        return parent

    def mknod(self, path, mode, dev, **kwargs):
        nodes = self.path_nodes(path)
        raise FuseOSError(EROFS)

    def open(self, path, flags, **kwargs):
        nodes = self.path_nodes(path)
        if type(nodes[-1]) == unicode:
            raise FuseOSError(ENOENT, http_status=404)

        return 0

    def opendir(self, path, **kwargs):
        nodes = self.path_nodes(path)
        return 0

    def read(self, path, size, offset, fh, **kwargs):
        nodes = self.path_nodes(path)
        if type(nodes[-1]) == unicode:
            raise FuseOSError(ENOENT, http_status=404)
        return {}

    def readdir(self, path, fh, **kwargs):
        nodes = self.path_nodes(path)
        if type(nodes[-1]) == unicode:
            raise FuseOSError(ENOENT, http_status=404)
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
        nodes = self.path_nodes(path)
        if type(nodes[-1]) == unicode:
            raise FuseOSError(ENOENT, http_status=404)
        return nodes[-1]

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
        nodes = self.path_nodes(path)
        if type(nodes[-1]) != unicode and ('overwrite' not in kwargs or not kwargs['force']):
            raise FuseOSError(EEXIST, http_status=400)
        if len(nodes) > 1 and type(nodes[-2]) == unicode and ('force' not in kwargs or not kwargs['force']):
            raise FuseOSError(ENOENT, http_status=404)
        parent = None
        for node in nodes[-1]:
            if type(node) != unicode:
                # 检查是否为文件夹
                if not S_ISDIR(node.underlying.get(u'mode')):
                    raise FuseOSError(ENOTDIR, http_status=400)
                parent = node
                continue
            # TODO 检查权限
            folder_document = self.create_document(node, parent, kwargs['mode'], mask=S_IFDIR, **kwargs)
            self.mongo.db.files.insert(folder_document)
            parent = self.create_node(folder_document)
        if type(nodes[-1]) == unicode:
            file_document = self.create_document(nodes[-1], parent, kwargs['mode'], mask=S_IFREG, **kwargs)
            file_node = self.create_node(file_document)
        else:
            file_node = nodes[-1]
        self.mongo.save_file(file_node.name, data)
        if type(nodes[-1]) == unicode:
            self.mongo.db.files.insert(file_node.underlying)
        else:
            now = datetime.datetime.now()
            file_node[u'atime'] = now
            file_node[u'mtime'] = now
            self.mongo.db.files.update_one({u'_id': file_node[u'_id']}, {u'$set': {u'atime': now, u'mtime': now}})
        return file_node

    def getfacl(self, path, **kwargs):
        raise FuseOSError(EOPNOTSUPP)

    def setfacl(self, path, ace, **kwargs):
        raise FuseOSError(EOPNOTSUPP)
