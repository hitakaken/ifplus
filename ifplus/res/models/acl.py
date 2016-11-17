# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from errno import *
import stat
from ..base.operations import FuseOSError


M_NONE = 0b00000000  # 无权限
M_READ = 0b10000000  # 读取
M_WRITE = 0b01000000  # 写入
M_EXECUTE = 0b00100000  # (读取和)执行
M_LIST_S = 0b10100000  # 列出文件夹内容
M_DELETE = 0b00010000  # 特殊权限（删除）
M_CHANGE = 0b00000100  # 特殊权限（权限控制）
M_XWRITE = 0b00000010  # 特殊权限 (扩展属性)
M_TWRITE = 0b00000001  # 特殊权限 (标签)
M_SPECIAL = 0b00001111  # 特殊权限（除删除外）
M_ACTION = 0b11101111  # 完全权限
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

    def apply_remove(self, user, sid):
        if self.get_ace(sid) is None:
            raise FuseOSError(ENOENT)
        if self.is_grantable(user, M_CONTROL):
            raise FuseOSError(EPERM)
        self.remove(sid)

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

    @staticmethod
    def sids_of(user):
        if user is None or user.is_anonymous:
            return []
        return user.sids()

    def _is_owner(self, sids):
        """内部：是否为所有者"""
        return self.owner() in sids

    def is_owner(self, user):
        """是否为所有者"""
        return self._is_owner(self.sids_of(user))

    def _is_group(self, sids):
        """内部：是否为所有组"""
        return self.group() in sids

    def is_group(self, user):
        """是否为所有组"""
        return self._is_group(self.sids_of(user))

    def perms(self, user):
        """获取当前用户权限"""
        if user is not None and user.is_admin:
            return M_CONTROL, M_NONE, M_CONTROL
        allowed = M_NONE
        denied = M_NONE
        grantable = M_NONE
        sids = self.sids_of(user)
        mode = stat.S_IMODE(self.mode())
        if self._is_owner(sids):
            if (mode & stat.S_IRUSR) > 0:
                allowed |= M_READ
            if (mode & stat.S_IWUSR) > 0:
                allowed |= M_WRITE
            if (mode & stat.S_IXUSR) > 0:
                allowed |= M_EXECUTE
            allowed |= M_SPECIAL
            grantable |= M_CONTROL
        if self.is_group(sids):
            if (mode & stat.S_IRGRP) > 0:
                allowed |= M_READ
            if (mode & stat.S_IWGRP) > 0:
                allowed |= M_WRITE
            if (mode & stat.S_IXGRP) > 0:
                allowed |= M_EXECUTE
        for ace in self.aces():
            if ace.get('sid') in sids:
                allowed |= (ace.get('allow', M_NONE) & ~denied)
                denied |= (ace.get('deny', M_NONE) & ~allowed)
                grantable |= ace.get('grant', M_NONE)
        other = M_NONE
        if(mode & stat.S_IROTH) > 0:
            other |= M_READ
        if (mode & stat.S_IWOTH) > 0:
            other |= M_WRITE
        if (mode & stat.S_IXOTH) > 0:
            other |= M_EXECUTE
        allowed |= other & ~denied
        return allowed, denied, grantable

    def is_allowed(self, user, mask):
        """判断：权限掩码是否被允许"""
        allowed, denied, grantable = self.perms(user)
        return (allowed & mask) > 0 and (denied & mask) == 0

    def is_denied(self, user, mask):
        """判断：权限掩码是否被拒绝"""
        allowed, denied, grantable = self.perms(user)
        return (denied & mask) > 0

    def is_grantable(self, user, mask):
        """判断：权限掩码是否可授权"""
        allowed, denied, grantable = self.perms(user)
        return (grantable & mask) > 0

    def apply_allow(self, user, sid, mask):
        """动作：授权允许"""
        if not self.is_grantable(user, mask):
            raise FuseOSError(EPERM)
        self.allow(sid, mask)

    def apply_undo_allow(self, user, sid, mask):
        """动作：取消授权允许"""
        if not self.is_grantable(user, mask):
            raise FuseOSError(EPERM)
        self.undo_allow(sid, mask)

    def apply_deny(self, user, sid, mask):
        """动作：授权拒绝"""
        if not self.is_grantable(user, mask):
            raise FuseOSError(EPERM)
        self.deny(sid, mask)

    def apply_undo_deny(self, user, sid, mask):
        """动作：取消授权拒绝"""
        if not self.is_grantable(user, mask):
            raise FuseOSError(EPERM)
        self.undo_deny(sid, mask)

    def apply_grant(self, user, sid, mask):
        """动作：授权管理"""
        if not self.is_grantable(user, mask):
            raise FuseOSError(EPERM)
        self.grant(sid, mask)

    def apply_undo_grant(self, user, sid, mask):
        """动作：取消授权管理"""
        if not self.is_grantable(user, mask):
            raise FuseOSError(EPERM)
        self.undo_grant(sid, mask)

