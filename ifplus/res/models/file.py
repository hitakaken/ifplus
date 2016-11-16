# -*- coding: utf-8 -*-
# https://github.com/Voronenko/Storing_TreeView_Structures_WithMongoDB
import stat
from pymongo import IndexModel, ASCENDING, DESCENDING
from ifplus.restful.patched import fields

META_ATTRIBUTE_NAMES = ['fid', 'dev', 'nlink', 'size',
                        'mode', 'uid', 'gid', 'create', 'creator',
                        'atime', 'mtime', 'ctime']


class BaseFileNode(object):
    def __init__(self, underlying, filesystem=None):
        self.underlying = underlying
        self.filesystem = filesystem


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
            'name': fields.String(description='文件名', required=True),
            'fid': fields.String(description='唯一标识', required=True),
            'mode': fields.Integer(description='文件模式', required=True),
            'dev': fields.String(description='所在设备'),
            'nlink': fields.Integer(description='链接数', required=True),
            'owner': fields.String(description='拥有者'),
            'group': fields.String(description='所在组'),
            'size': fields.Integer(description='文件大小', required=True),
            'access': fields.Integer(description='最后访问时间', required=True),
            'modify': fields.Integer(description='最后修改时间', required=True),
            'change': fields.Integer(description='最后变更时间', required=True),
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
        if attr_name == 'ctype':
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


class FileXAttrs(BaseFileNode):
    def __init__(self, underlying, filesystem=None):
        super(FileXAttrs, self).__init__(underlying, filesystem=filesystem)

    def __getattr__(self, attr_name):
        raise AttributeError

    def __setattr__(self, key, value):
        raise AttributeError


class FileStorage(BaseFileNode):
    def __init__(self, underlying, filesystem=None):
        super(FileStorage, self).__init__(underlying, filesystem=filesystem)

    def __getattr__(self, attr_name):
        raise AttributeError

    def __init__(self,
                 meta,  # 基本信息
                 content,  # 内容信息
                 xattrs,  # 扩展属性
                 path,   # 路径
                 parent,  # 父节点
                 left,   # 左序
                 right  # 右序
                 ):
        pass


class FileObject(object):
    def __init__(self, path, storage=None):
        pass

    def load(self):
        pass


