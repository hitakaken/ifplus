# -*- coding: utf-8 -*-
# https://github.com/Voronenko/Storing_TreeView_Structures_WithMongoDB
import stat
from pymongo import IndexModel, ASCENDING, DESCENDING
from ifplus.restful.patched import fields


class FileMetaInfo(object):
    def __init__(self,
                 name=None, fid=None, dev=None,
                 mode=None, uid=None, gid=None,
                 nlink=None, size=None,
                 atime=None, mtime=None, ctime=None,
                 create=None, creator=None):
        self.name = name
        self.fid = fid
        self.dev = dev
        self.mode = mode
        self.uid = uid
        self.gid = gid
        self.nlink = nlink
        self.size = size
        self.atime = atime
        self.mtime = mtime
        self.ctime = ctime
        self.create = create
        self.creator = creator

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

    @classmethod
    def parse(cls, raw):
        """解析原始记录(Mongo, ES等)"""
        return FileMetaInfo(
            name=raw['name'], fid=raw['_id'], dev=raw['dev'] if 'dev' in raw else None,
            mode=raw['mode'], uid=raw['uid'] if 'uid' in raw else None, gid=raw['gid'] if 'gid' in raw else None,
            nlink=raw['nlink'], size=raw['size'],
            atime=raw['atime'], mtime=raw['mtime'], ctime=raw['ctime'],
            create=raw['create'] if 'create' in raw else None, creator=raw['creator'] if 'creator' in raw else None
        )


class FileContent(object):
    def __init__(self, type):
        pass


class FileXAttrs(object):
    def __init__(self):
        pass


class FileStorage(object):
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


