# -*- coding: utf-8 -*-
import datetime
import stat
import os.path
from bidict import bidict
from .base import BaseFileNode
from ifplus.data.helpers import time_utils

MANAGED_ATTRIBUTE_NAMES = bidict({
    # 文件定位信息
    u'fid': u'_id', u'dev': u'dev', u'name': u'name', u'ancestors': u'ancestors',
    # 文件权限信息
    u'owner': u'uid', u'group': u'gid', u'mode': u'mode',
    # 文件大小信息
    u'nlink': u'nlink', u'size': u'size',
    # 文件时间信息
    u'access': u'atime', u'modify': u'mtime', u'change': u'ctime',
    # 文件创建信息
    u'create': u'create', u'creator': u'creator'
})


class FileINode(BaseFileNode):
    """文件 INode 工具类"""
    def __init__(self, underlying, vfs=None):
        super(FileINode, self).__init__(underlying, vfs=vfs)

    def init_inode(self, name, times, user=None):
        """初始化文件INode属性"""
        if u'name' not in self.underlying:
            self.underlying[u'name'] = name
        if u'mtime' not in self.underlying:
            self.underlying[u'mtime'] = times
        if u'ctime' not in self.underlying:
            self.underlying[u'ctime'] = times
        if u'atime' not in self.underlying:
            self.underlying[u'atime'] = times
        if u'create' not in self.underlying:
            self.underlying[u'create'] = times
        if u'creator' not in self.underlying and user is not None:
            self.underlying[u'creator'] = user.sid
        if u'uid' not in self.underlying and user is not None:
            self.underlying[u'uid'] = user.sid
        if u'gid' not in self.underlying and user is not None:
            self.underlying[u'gid'] = user.sid
        if u'nlink' not in self.underlying:
            self.underlying[u'nlink'] = 1
        if u'size' not in self.underlying:
            self.underlying[u'size'] = 0
        return self

    @property
    def id(self):
        return self.underlying[u'_id']

    @property
    def file_id(self):
        """文件唯一标识"""
        return str(self.underlying[u'_id']) if self.underlying[u'_id'] is not None else None

    @property
    def fid(self):
        return str(self.file_id)

    @file_id.setter
    def file_id(self, file_id):
        """设置文件唯一标识"""
        if self.file_id is not None and self.file_id != str(file_id):
            self.underlying[u'_id'] = file_id
            self.changes[u'inodes'].add(u'_id')

    @property
    def dev(self):
        """文件对象所在设备"""
        return self.underlying.get(u'dev', None)

    @dev.setter
    def dev(self, dev):
        """设置文件对象所在设备"""
        if self.dev != dev:
            self.underlying[u'dev'] = dev
            self.changes[u'inodes'].add(u'dev')

    @property
    def name(self):
        """文件名"""
        return self.underlying[u'name']

    @property
    def splitext(self):
        """文件名分隔"""
        prefix, suffix = os.path.splitext(self.name)
        return prefix, suffix

    @property
    def ext_name(self):
        """文件扩展名"""
        prefix, suffix = self.splitext
        return suffix

    @property
    def ancestors(self):
        """祖先节点"""
        return self.underlying.get(u'ancestors', [])

    @property
    def uid(self):
        """文件所有者"""
        return self.underlying.get(u'uid', None)

    @uid.setter
    def uid(self, uid):
        """设置文件所有者"""
        if self.uid != uid:
            self.underlying[u'uid'] = uid
            self.changes[u'inodes'].add(u'uid')

    @property
    def owner(self):
        """文件所有者"""
        return self.uid

    @owner.setter
    def owner(self, owner):
        """设置文件所有者"""
        self.uid = owner

    @property
    def gid(self):
        """文件所有组"""
        return self.underlying.get(u'gid', None)

    @gid.setter
    def gid(self, gid):
        """设置文件所有者"""
        if self.gid != gid:
            self.underlying[u'gid'] = gid
            self.changes[u'inodes'].add(u'gid')

    @property
    def group(self):
        """文件所有组"""
        return self.gid

    @group.setter
    def group(self, group):
        """设置文件所有者"""
        self.gid = group

    @property
    def mode(self):
        """文件权限掩码"""
        return self.underlying[u'mode']

    @mode.setter
    def mode(self, mode):
        if self.gid != mode:
            """文件权限掩码"""
            self.underlying[u'mode'] = mode
            self.changes[u'inodes'].add(u'mode')

    @property
    def is_file(self):
        """是否普通文件"""
        return stat.S_ISREG(self.mode)

    @property
    def is_folder(self):
        """是否目录文件"""
        return stat.S_ISDIR(self.mode)

    @property
    def is_link(self):
        """是否符号链接"""
        return stat.S_ISLNK(self.mode)

    @property
    def is_block_special(self):
        """是否块设备"""
        return stat.S_ISBLK(self.mode)

    @property
    def is_character_special(self):
        """是否字符设备"""
        return stat.S_ISCHR(self.mode)

    @property
    def is_fifo(self):
        """是否命名管道"""
        return stat.S_ISFIFO(self.mode)

    @property
    def is_socket(self):
        """是否套接字"""
        return stat.S_ISSOCK(self.mode)

    @property
    def nlink(self):
        """文件链接数，有多少个路径指向该文件对象"""
        return self.underlying.get(u'nlink', 1)

    @nlink.setter
    def nlink(self, nlink):
        if self.nlink != nlink:
            self.underlying[u'nlink'] = nlink
            self.changes[u'inodes'].add(u'nlink')

    @property
    def size(self):
        """文件大小，文件夹及链接始终为 0"""
        return self.underlying.get(u'size', 0)

    @size.setter
    def size(self, size):
        if self.size != size:
            self.underlying[u'size'] = size
            self.changes[u'inodes'].add(u'size')

    @property
    def atime(self):
        """文件最后访问时间，访问定义：文件夹浏览，文件内容读取，链接跳转"""
        return self.underlying.get(u'atime', None)

    @property
    def access(self):
        """文件最后访问时间，访问定义：文件夹浏览，文件内容读取，链接跳转"""
        return self.atime

    def visited(self, atime=None):
        if atime is None:
            atime = datetime.datetime.utcnow()
        self.underlying[u'atime'] = atime
        self.changes[u'inodes'].add(u'atime')

    @property
    def mtime(self):
        """文件最后修改时间，修改定义：文件夹内新增删除，文件内容修改，链接目标修改"""
        return self.underlying.get(u'mtime', None)

    @property
    def modify(self):
        """文件最后修改时间，修改定义：文件夹内新增删除，文件内容修改，链接目标修改"""
        return self.mtime

    def modified(self, mtime=None):
        if mtime is None:
            mtime = datetime.datetime.utcnow()
        self.underlying[u'mtime'] = mtime
        self.changes[u'inodes'].add(u'mtime')

    @property
    def ctime(self):
        """文件最后变更时间，变更定义：文件对象权限、扩展属性等修改"""
        return self.underlying.get(u'ctime', None)

    @property
    def change(self):
        """文件最后变更时间，变更定义：文件对象权限、扩展属性等修改"""
        return self.ctime

    def changed(self, ctime=None):
        if ctime is None:
            ctime = datetime.datetime.utcnow()
        self.underlying[u'ctime'] = ctime
        self.changes[u'inodes'].add(u'ctime')

    @property
    def create(self):
        """文件创建时间"""
        return self.underlying.get(u'create', None)

    @property
    def creator(self):
        """文件创建者"""
        return self.underlying.get(u'creator', None)

    def get_inodes(self, result=None):
        """输出INode信息"""
        if result is None:
            result = {}
        strs = bin(self.mode)[-9:]
        mode_array = [
            [int(strs[0]),int(strs[1]),int(strs[2])],
            [int(strs[3]),int(strs[4]),int(strs[5])],
            [int(strs[6]),int(strs[7]),int(strs[8])]]
        result.update({
            u'fid': self.fid,
            u'dev': self.dev,
            u'name': self.name,
            u'owner': self.vfs.lookup_user(self.owner),
            u'group': self.vfs.lookup_user(self.group),
            u'ftype': (u'%06o' % (0o0177777 & self.mode))[:2],
            u'mode': mode_array,
            u'nlink': self.nlink,
            u'size': self.size,
            u'access': time_utils.timestamp(self.access),
            u'modify': time_utils.timestamp(self.modify),
            u'change': time_utils.timestamp(self.change),
            u'create': time_utils.timestamp(self.create),
            u'creator': self.vfs.lookup_user(self.creator)
        })
        return result

    def record_inodes(self):
        """将inode信息记录到临时结果"""
        self.result = self.get_inodes(result=self.result)
        return self
