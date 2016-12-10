# -*- coding: utf-8 -*-
import copy
import dpath.util
from errno import EPERM
from ...base.operations import FuseOSError
from .acls import FileAcls, M_XWRITE


class FileXattrs(FileAcls):
    """文件扩展属性工具类"""
    def __init__(self, underlying, vfs=None):
        super(FileXattrs, self).__init__(underlying, vfs=vfs)

    def init_xattrs(self):
        """初始化文件扩展属性"""
        if u'xattrs' not in self.underlying:
            self.underlying[u'xattrs'] = {
                u'user': {},
                u'system': {},
            }
        return self

    @property
    def xattrs(self):
        """获取扩展属性"""
        return self.underlying[u'xattrs']

    def update_xattrs(self, xattrs, user=None, perms=None, ctime=None):
        """更新扩展属性"""
        allow, deny, grant = self.user_perms(user=user, perms=perms)
        if allow & M_XWRITE == 0:
            raise FuseOSError(EPERM)
        new_xattrs = copy.deepcopy(self.xattrs)
        for (namespace, attrs) in xattrs.items():
            if namespace not in new_xattrs:
                new_xattrs[namespace] = {}
            for (k, v) in attrs.items():
                if v is None:
                    if k in new_xattrs[namespace]:
                        new_xattrs[namespace].pop(k, None)
                else:
                    new_xattrs[namespace][k] = v
            self.changes[u'xattrs'].add(namespace)
        self.changed(ctime=ctime)
        self.underlying[u'xattrs'] = new_xattrs

    def remove_xattrs(self, namespaces, user=None, perms=None, ctime=None):
        """删除扩展属性命名空间"""
        allow, deny, grant = self.user_perms(user=user, perms=perms)
        if allow & M_XWRITE == 0:
            raise FuseOSError(EPERM)
        new_xattrs = copy.deepcopy(self.xattrs)
        for namespace in namespaces:
            new_xattrs.pop(namespace, None)
            self.changes[u'xattrs'].add(namespace)
        self.changed(ctime=ctime)
        self.underlying[u'xattrs'] = new_xattrs

    def get_xattrs(self, result=None, namespaces=None, attrnames=None):
        """获取扩展属性"""
        if result is None:
            result = {}
        new_xattrs = {}
        if namespaces is not None:
            for namespace in namespaces:
                if namespace in self.underlying[u'xattrs']:
                    new_xattrs[namespace] = self.underlying[u'xattrs'][namespace]
        for attrname in attrnames:
            try:
                value = dpath.util.get(self.xattrs, attrname, separator='.')
                dpath.util.set(new_xattrs, attrname, value, separator='.')
            except KeyError:
                pass
        result.update({
            u'xattrs': new_xattrs
        })
        return result

    def record_xattrs(self, namespaces=None, attrnames=None):
        """记录扩展属性到临时结果"""
        self.result = self.get_xattrs(result=self.result, namespaces=namespaces, attrnames=attrnames)
        return self
