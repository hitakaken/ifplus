# -*- coding: utf-8 -*-import six
from errno import EPERM
from ..exceptions import FuseOSError
from .inodes import FileINode

M_NONE = 0b00000000  # 无权限
M_READ = 0b10000000  # 读取
M_WRITE = 0b01000000  # 写入(内容)
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


def record_old(old_aces, changes):
    for ace in old_aces:
        sid = ace[u'sid']
        if sid not in changes:
            changes[sid] = {}
        changes[sid][u'old'] = ace[u'mask']
    return changes


def convert_permission_binary_to_array(mask):
    array = [int(m) for m in bin(mask)[10:]]
    return [[array[x], array[x + 8], array[x + 16]] for x in range(0, 8)]


def check_changes(changes, grant):
    change_mask = 0x00
    for (sid, ace) in changes.items():
        if u'old' in ace and u'new' in ace:
            change = ace[u'old'] ^ ace[u'new']
            change_mask |= ((change & 0xFF0000) >> 16) | ((change & 0xFF00) >> 8) | (change & 0xFF)
        elif u'old' in ace and u'new' not in ace:
            change_mask |= ((ace[u'old'] & 0xFF0000) >> 16) | ((ace[u'old'] & 0xFF00) >> 8) | (ace[u'old'] & 0xFF)
        elif u'new' in ace and u'old' not in ace:
            change_mask |= ((ace[u'new'] & 0xFF0000) >> 16) | ((ace[u'new'] & 0xFF00) >> 8) | (ace[u'new'] & 0xFF)
    if (change_mask & ~grant) > 0:
        raise FuseOSError(EPERM)


class FileAcls(FileINode):
    """文件权限工具类"""

    def __init__(self, underlying, vfs=None):
        super(FileAcls, self).__init__(underlying, vfs=vfs)

    def init_acl(self, inherit=None):
        """初始化文件ACL权限属性"""
        if u'acl' not in self.underlying:
            self.underlying[u'acl'] = inherit if inherit is not None else []
        return self

    @property
    def acl(self):
        """底层权限控制列表"""
        return self.underlying.get(u'acl', [])

    @property
    def inherits(self):
        """可被继承的ACL权限"""
        inherits = []
        for ace in self.acl:
            if ace[u'mask'] & 0x01000000 > 0:
                inherits.append({
                    u'sid': ace[u'sid'],
                    u'mask': ace[u'mask'] | 0x02000000
                })
        return inherits

    @acl.setter
    def acl(self, aces):
        """设置底层权限控制列表"""
        self.underlying[u'acl'] = aces
        self.changes[u'acl'] = True

    def update_acl(self, aces, user=None, perms=None, ctime=None):
        """更新ACL权限列表"""
        allow, deny, grant = self.user_perms(user=user, perms=perms)
        if allow & M_PWRITE == 0:
            raise FuseOSError(EPERM)
        changes = record_old(list(self.acl), {})
        new_aces = []
        for ace in aces:
            sid = ace[u'sid']
            if sid not in changes:
                changes[sid] = {}
            mask = int(str(u'100000' + u''.join(ace[u'mask'])), 2)
            changes[sid][u'new'] = mask
            new_aces.append({u'sid': sid, u'mask': mask})
        check_changes(changes, grant)
        self.changed(ctime=ctime)
        self.acl = new_aces

    def append_acl(self, aces, user=None, perms=None, ctime=None):
        """添加ACL权限"""
        allow, deny, grant = self.user_perms(user=user, perms=perms)
        if allow & M_PWRITE == 0:
            raise FuseOSError(EPERM)
        old_aces = list(self.acl)
        changes = record_old(old_aces, {})
        for ace in aces:
            sid = ace[u'sid']
            if sid not in changes:
                changes[sid] = {}
            mask = int(str(u'100000' + u''.join(ace[u'mask'])), 2)
            changes[sid][u'new'] = mask
        for (sid, change) in changes.items():
            if u'old' in change and u'new' not in change:
                changes[sid][u'new'] = change[u'old']
        check_changes(changes, grant)
        new_aces = []
        for ace in old_aces:
            sid = ace[u'sid']
            mask = changes[sid][u'new']
            new_aces.append({u'sid': sid, u'mask': mask})
        for ace in aces:
            sid = ace[u'sid']
            if u'old' not in changes[sid]:
                mask = changes[sid][u'new']
                new_aces.append({u'sid': sid, u'mask': mask})
        self.changed(ctime=ctime)
        self.acl = new_aces

    def remove_acl(self, sids, user=None, perms=None, ctime=None):
        """删除ACL权限"""
        allow, deny, grant = self.user_perms(user=user, perms=perms)
        if allow & M_PWRITE == 0:
            raise FuseOSError(EPERM)
        old_aces = list(self.acl)
        changes = record_old(old_aces, {})
        for (sid, change) in changes.items():
            if sid not in sids:
                changes[sid][u'new'] = changes[u'old']
        check_changes(changes, grant)
        new_aces = []
        for ace in old_aces:
            if ace[u'sid'] not in sids:
                new_aces.append(ace)
        self.changed(ctime=ctime)
        self.acl = new_aces

    def is_owner(self, user=None):
        """是否文件所有者"""
        return user is not None and not user.is_anonymous and self.owner is not None and self.owner in user.sids

    def is_group(self, user=None):
        """是否文件所在组"""
        return user is not None and not user.is_anonymous and self.group is not None and self.group in user.sids

    def is_full_controller(self, user=None, perms=None):
        """是否具有完全控制权限"""
        allow, deny, grant = self.user_perms(user=user, perms=perms)
        return grant & 0xFF > 0

    def user_perms(self, user=None, perms=None):
        return self.perms(user=user) if perms is None else perms

    def perms(self, user=None):
        """获取用户权限"""
        allow = 0x00
        deny = 0x00
        grant = 0x00
        if user is not None and not user.is_anonymous and user.is_admin:
            return 0xFF, 0x00, 0xFF
        if self.is_owner(user=user):
            grant |= 0xFF
            allow |= self.mode & 0o700 >> 1
            allow |= 0x1F
        if self.is_group(user=user):
            allow |= self.mode & 0o070 << 2
        # 遍历ACL条目
        if user is not None and not user.is_anonymous:
            for ace in self.acl:
                if ace[u'sid'] in user.sids:
                    e_allow = (ace[u'mask'] & 0xFF0000) >> 16  # 当前ACL条目允许的权限
                    e_deny = (ace[u'mask'] & 0xFF00) >> 8  # 当前ACL条目拒绝的权限
                    e_grant = (ace[u'mask'] & 0xFF)  # 当前ACL条码可授权的权限
                    allow |= e_allow & ~deny  # 计算后的允许权限
                    deny |= e_deny & ~allow  # 计算后的拒绝权限
                    grant |= e_grant  # 计算后的可授权权限
        allow |= self.mode & 0o007 << 5
        return allow, deny, grant

    def perms_mask(self, user=None):
        allow, deny, grant = self.perms(user=user)
        return 0x80000000 | (allow << 16) | (deny << 8) | grant

    def get_acl(self, result=None):
        """获取用户ACL权限列表"""
        if result is None:
            result = {}
        result.update({
            u'acl': [{
                         u'sid': self.vfs.lookup_user(ace[u'sid']),
                         u'perms': convert_permission_binary_to_array(ace[u'mask']),
                         u'inherit': 1 if ace[u'mask'] & 0x01000000 > 0 else 0
                     }
                     for ace in self.acl]})
        return result

    def get_perms(self, result=None, user=None):
        """获取用户权限"""
        if result is None:
            result = {}
        result.update({
            u'perms': convert_permission_binary_to_array(self.perms_mask(user=user))
        })
        return result

    def record_acl(self):
        """记录用户ACL权限列表到临时结果"""
        self.result = self.get_acl(result=self.result)
        return self

    def record_perms(self, user=None):
        """记录用户权限到临时结果"""
        self.result = self.get_perms(result=self.result, user=user)
        return self
