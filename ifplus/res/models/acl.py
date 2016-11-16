# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

M_NONE = 0b00000000  # 无权限
M_READ = 0b10000000  # 读取
M_WRITE = 0b01000000  # 写入
M_EXECUTE = 0b00100000  # (读取和)执行
M_LIST_S = 0b10100000  # 列出文件夹内容
M_DELETE = 0b00010000  # 特殊权限（删除）
M_CHANGE = 0b00000100  # 特殊权限（权限控制）
M_XWRITE = 0b00000010  # 特殊权限 (扩展属性)
M_TWRITE = 0b00000001  # 特殊权限 (标签)
M_CONTROL = 0b11111111  # 完全控制


class AccessControlList(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def owner(self):
        pass

    @abstractmethod
    def group(self):
        pass
    
    @abstractmethod
    def mode(self):
        pass

    @abstractmethod
    def aces(self):
        return []

    @abstractmethod
    def add_or_update(self, sid, allow_mask, deny_mask, grant_mask, inheritable, inherited):
        """增加ACL条目"""
        pass

    def add_or_update_ace(self, ace):
        self.add_or_update(ace['sid'],
                           ace.get('allow', M_NONE), ace.get('deny', M_NONE), ace.get('grant', M_NONE),
                           ace.get('ihb', False), ace.get('ihd', False))

    @abstractmethod
    def remove(self, sid):
        pass

    def get_ace(self, sid):
        for ace in self.aces():
            if ace.get('sid') == sid:
                return ace
        return None

    @staticmethod
    def base_ace(sid):
        return {
            'sid': sid,
            'allow': M_NONE,
            'deny': M_NONE,
            'grant': M_NONE,
            'ihb': False,
            'ihd': False
        }

    def allow(self, sid, mask):
        """变更：允许权限掩码"""
        ace = self.get_ace(sid)
        if ace is None:
            ace = self.base_ace(sid)
        ace['allow'] |= mask
        ace['deny'] &= ~mask
        self.add_or_update_ace(ace)

    def undo_allow(self, sid, mask):
        """变更：取消允许权限掩码"""
        ace = self.get_ace(sid)
        if ace is None:
            ace = self.base_ace(sid)
        ace['allow'] &= ~mask
        self.add_or_update_ace(ace)

    def deny(self, sid, mask):
        """变更：拒绝权限掩码"""
        ace = self.get_ace(sid)
        if ace is None:
            ace = self.base_ace(sid)
        ace['deny'] |= mask
        ace['allow'] &= ~mask
        self.add_or_update_ace(ace)

    def undo_deny(self, sid, mask):
        """变更：取消拒绝权限掩码"""
        ace = self.get_ace(sid)
        if ace is None:
            ace = self.base_ace(sid)
        ace['deny'] &= ~mask
        self.add_or_update_ace(ace)

    def grant(self, sid, mask):
        """变更：赋予授权权限掩码"""
        ace = self.get_ace(sid)
        if ace is None:
            ace = self.base_ace(sid)
        ace['grant'] |= mask
        self.add_or_update_ace(ace)

    def undo_grant(self, sid, mask):
        """变更：取消赋予授权权限掩码"""
        ace = self.get_ace(sid)
        if ace is None:
            ace = self.base_ace(sid)
        ace['grant'] &= ~mask
        self.add_or_update_ace(ace)

    def inherit_acl(self):
        """获取继承的ACL条目"""
        inherits = []
        for ace in self.aces():
            if ace.get('inheritable', False):
                inherits.append({
                    'sid': ace.get('sid'),
                    'allow': ace.get('allow'),
                    'deny': ace.get('deny'),
                    'grant': ace.get('grant'),
                    'ihb': True,
                    'ihd': True
                })
        return inherits

    def perms(self, user):
        """获取当前用户权限"""
        sids = user.sids()

        pass
