# -*- coding: utf-8 -*-
from .inodes import FileINode

M_NONE = 0b00000000  # 无权限
M_READ = 0b10000000  # 读取
M_WRITE = 0b01000000  # 写入
M_EXECUTE = 0b00100000  # (读取和)执行
M_LIST_S = 0b10100000  # 列出文件夹内容
M_DELETE = 0b00010000  # 特殊权限（删除）
M_PWRITE = 0b00001000  # 特殊权限（权限控制）
M_XWRITE = 0b00000100  # 特殊权限 (扩展属性)
M_TWRITE = 0b00000010  # 特殊权限 (反馈)
M_RESERV = 0b00000001  # 特殊权限（保留）
M_SPECIAL = 0b00001111  # 特殊权限（除删除外）
M_ACTION = 0b11101111  # 完全权限
M_CONTROL = 0b11111111  # 完全控制


class FileAcls(FileINode):
    """文件权限工具类"""
    def __init__(self, underlying, vfs=None):
        super(FileAcls, self).__init__(underlying, vfs=vfs)

    @property
    def acl(self):
        """底层权限控制列表"""
        return self.underlying.get(u'acl', [])

    def is_owner(self, user=None):
        """是否文件所有者"""
        return user is not None and not user.is_anonymous and self.owner is not None and self.owner in user.sids

    def perms(self, user=None):
        """获取用户权限"""
        return None

    def get_acl(self, result=None):
        """获取用户ACL权限列表"""
        if result is None:
            result = {}
        result.update({
            u'acl': [{u'sid': ace[u'sid'], u'mask': [int(m) for m in bin(ace[u'mask'])[16:]]}
                     for ace in self.acl]})
        return result

    def get_perms(self, result=None, user=None):
        if result is None:
            result = {}
        return result

    def record_acl(self):
        self.result = self.get_acl(result=self.result)
        return self

    def record_perms(self, user=None):
        self.result = self.get_perms(result=self.result)
        return self

