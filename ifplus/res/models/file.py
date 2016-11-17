# -*- coding: utf-8 -*-
# https://github.com/Voronenko/Storing_TreeView_Structures_WithMongoDB
import stat
from pymongo import IndexModel, ASCENDING, DESCENDING
from ifplus.restful.patched import fields
from .acl import AccessControlList

META_ATTRIBUTE_NAMES = ['fid', 'dev', 'nlink', 'size',
                        'mode', 'uid', 'gid', 'create', 'creator',
                        'atime', 'mtime', 'ctime']


class BaseFileNode(object):
    def __init__(self, underlying, filesystem=None):
        self.underlying = underlying
        self.filesystem = filesystem

    def meta(self):
        self.__class__ = FileMetaInfo
        return self

    def contents(self):
        self.__class__ = FileContent
        return self

    def xattrs(self):
        self.__class__ = FileExtraAttributes
        return self

    def acl(self):
        self.__class__ = FileAccessControlList
        return self

    def node(self):
        self.__class__ = FileTreeNode
        return self


class FileMetaInfo(BaseFileNode):
    def __init__(self, underlying, filesystem=None):
        super(FileMetaInfo, self).__init__(underlying, filesystem=filesystem)

    def __getattr__(self, attr_name):
        if attr_name in META_ATTRIBUTE_NAMES:
            return self.underlying.get(attr_name, None)
        raise AttributeError

    def __setattr__(self, key, value):
        if key in META_ATTRIBUTE_NAMES:
            self.underlying[key] = value
        raise AttributeError

    def is_file(self):
        """是否普通文件"""
        return stat.S_ISREG(self.mode)

    def is_folder(self):
        """是否目录文件"""
        return stat.S_ISDIR(self.mode)

    def is_link(self):
        """是否符号链接"""
        return stat.S_ISLNK(self.mode)

    def is_block_special(self):
        """是否块设备"""
        return stat.S_ISBLK(self.mode)

    def is_character_special(self):
        """是否字符设备"""
        return stat.S_ISCHR(self.mode)

    def is_fifo(self):
        """是否命名管道"""
        return stat.S_ISFIFO(self.mode)

    def is_socket(self):
        """是否套接字"""
        return stat.S_ISSOCK(self.mode)

    @classmethod
    def model(cls, api):
        """Swagger UI Model"""
        return api.model('FileMetaInfo', {
            'name': fields.String(title='文件名', description='文件名', required=True),
            'fid': fields.String(description='唯一标识', required=True),
            'mode': fields.Integer(description='文件模式', required=True),
            'dev': fields.String(description='所在设备'),
            'nlink': fields.Integer(description='链接数', required=True),
            'owner': fields.String(description='所有者'),
            'group': fields.String(description='所在组'),
            'size': fields.Integer(description='文件大小', required=True),
            'access': fields.Integer(description='最后访问时间', required=True),
            'modify': fields.Integer(title='最后修改时间', description='上一次文件内容变动的时间', required=True),
            'change': fields.Integer(title='最后变更时间', description='上一次文件信息变动的时间', required=True),
            'create': fields.Integer(description='创建时间'),
            'creator': fields.Integer(description='创建者'),
        })

    @property
    def as_dict(self):
        result = {
            'name': self.name, 'fid': self.fid,
            'mode': self.mode, 'nlink': self.nlink, 'size': self.size,
            'access': self.atime, 'modify': self.mtime, 'change': self.ctime
        }
        if self.dev is not None:
            result['dev'] = self.dev
        if self.uid is not None:
            result['owner'] = self.uid
        if self.gid is not None:
            result['group'] = self.gid
        if self.create is not None:
            result['create'] = self.create
        if self.creator is not None:
            result['creator'] = self.creator
        return result

    MONGO_INDEXES = [
        IndexModel([('mtime', DESCENDING)], name='last_modify'),
        IndexModel([('uid', ASCENDING), ('mtime', DESCENDING)], name='last_modify_by_user'),
        IndexModel([('ctime', DESCENDING)], name='last_change'),
        IndexModel([('uid', ASCENDING), ('ctime', DESCENDING)], name='last_change_by_user'),
        IndexModel([('ctime', DESCENDING), ('mtime', DESCENDING)], name='time_stamp'),
    ]

CONTENT_TYPE_UNKNOWN = 0
CONTENT_TYPE_EMBED_TEXT = 1
CONTENT_TYPE_EMBED_OBJECT = 2
CONTENT_TYPE_LOCAL = 3
CONTENT_TYPE_REMOTE = 4


class FileContent(BaseFileNode):
    def __init__(self, underlying, filesystem=None):
        super(FileContent, self).__init__(underlying, filesystem=filesystem)

    def __getattr__(self, attr_name):
        if attr_name == 'name':
            self.underlying.get('name')
        elif attr_name == 'ctype':
            self.underlying.get('ctype', CONTENT_TYPE_UNKNOWN)
        elif attr_name == 'content':
            content_type = self.underlying.get('ctype', CONTENT_TYPE_UNKNOWN)
            if content_type <= CONTENT_TYPE_EMBED_OBJECT:
                return self.underlying.get('content', None)
            elif self.filesystem is not None:
                return self.filesystem.read(self.underlying)
        raise AttributeError

    def __setattr__(self, key, value):
        if key == 'ctype':
            self.underlying[key] = value
        elif key == 'content':
            content_type = self.underlying.get('ctype', CONTENT_TYPE_UNKNOWN)
            if content_type == CONTENT_TYPE_UNKNOWN:
                if type(content_type) is str or type(content_type) is unicode:
                    self.underlying['ctype'] = CONTENT_TYPE_EMBED_TEXT
                elif type(content_type) is dict or type(content_type) is list:
                    self.underlying['ctype'] = CONTENT_TYPE_EMBED_OBJECT
            if content_type <= 2:
                self.underlying[key] = value
            elif self.filesystem is not None:
                self.filesystem.write(self.underlying, value)
        raise AttributeError

    @classmethod
    def model(cls, api):
        """Swagger UI Model"""
        return api.model('FileMetaInfo', {
            'name': fields.String(title='文件名', description='文件名', required=True),
            'ctype': fields.String(description='文件形式', required=True),
            'content': fields.String(description='文件内容', required=True)
        })


class FileExtraAttributes(BaseFileNode):
    def __init__(self, underlying, filesystem=None):
        super(FileExtraAttributes, self).__init__(underlying, filesystem=filesystem)

    def check(self):
        if 'xattrs' not in self.underlying:
            self.underlying['xattrs'] = {}

    @property
    def props(self):
        self.check()
        return self.underlying['xattrs']

    def __getattr__(self, attr_name):
        self.check()
        if attr_name in self.underlying['xattrs']:
            self.underlying['xattrs'].get(attr_name)
        raise AttributeError

    def __setattr__(self, key, value):
        self.check()
        self.underlying[key] = value


class FileAccessControlList(AccessControlList, BaseFileNode):
    def __init__(self, underlying, filesystem=None):
        super(FileAccessControlList, self).__init__(underlying, filesystem=filesystem)

    def owner(self):
        return self.underlying.get('uid', None)

    def group(self):
        return self.underlying.get('gid', None)

    def mode(self):
        return self.underlying.get('mode')

    def aces(self):
        return self.underlying.get('acl', [])

    def add_or_update(self, sid, allow_mask, deny_mask, grant_mask, inheritable, inherited):
        aces = []
        found = False
        new_ace = {'sid': sid,
                   'allow': allow_mask, 'deny': deny_mask, 'grant': grant_mask,
                   'ihb': inheritable, 'ihd': inherited}
        for ace in self.aces():
            if ace.get('sid') == sid:
                aces.append(new_ace)
                found = True
            else:
                aces.append(ace)
        if not found:
            aces.append(new_ace)
        self.underlying['acl'] = aces

    def remove(self, sid):
        aces = []
        for ace in self.aces():
            if ace.get('sid') != sid:
                aces.append(ace)
        self.underlying['acl'] = aces

    @classmethod
    def model(cls, api):
        """Swagger UI Model"""
        return api.mode("FileACL", {
            'owner': fields.String(description='所有者'),
            'group': fields.String(description='所在组'),
            'mode': fields.Integer(description='文件模式', required=True),
            'acl': fields.List(fields.String, description='ACL条目')
        })


class FileTreeNode(BaseFileNode):
    def __init__(self, underlying, filesystem=None):
        super(FileTreeNode, self).__init__(underlying, filesystem=filesystem)

    def __getattr__(self, attr_name):
        if attr_name in ['ancestors', 'left', 'right']:
            return self.underlying.get(attr_name, None)
        elif attr_name == 'path':
            paths = self.underlying.get('ancestors', [])
            paths.append(self.name)
            return u'/' + u'/'.join(paths)
        elif attr_name == 'parent_path':
            paths = self.underlying.get('ancestors', [])
            return u'/' + u'/'.join(paths)
        elif attr_name == 'parent':
            return FileObject(self.parent_path, filesystem=self.filesystem)
        raise AttributeError

    def __setattr__(self, key, value):
        if key in ['ancestors', 'left', 'right']:
            self.underlying[key] = value
        elif key == 'path':
            pass
        elif key == 'parent_path':
            pass
        elif key == 'parent':
            pass
        raise AttributeError


class FileObject(object):
    def __init__(self, path, underlying=None, filesystem=None):
        self.path = path
        self.underlying = underlying
        self.filesystem = filesystem

    def load(self):
        if self.underlying is None and self.filesystem is not None:
            self.underlying = self.filesystem.load(self.path)


