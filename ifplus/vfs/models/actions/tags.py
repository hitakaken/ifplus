# -*- coding: utf-8 -*-
from errno import EPERM
from ..exceptions import FuseOSError
from .acls import FileAcls, M_TWRITE


class FileTags(FileAcls):
    """文件标签工具类"""

    def __init__(self, underlying, vfs=None):
        super(FileTags, self).__init__(underlying, vfs=vfs)

    def init_tags(self):
        """初始化文件标签"""
        if u'tags' not in self.underlying:
            self.underlying[u'tags'] = []
        return self

    @property
    def tags(self):
        """文件标签列表"""
        tags = sorted(self.underlying.get(u'tags', []), key=lambda tag: len(tag[u'u']))
        return map(lambda tag: tag[u't'], tags)

    def user_tags(self, user=None):
        """用户标签列表"""
        if user is None or user.is_anonymous:
            return []
        tags = filter(lambda tag: user.sid in tag[u'u'], self.underlying.get(u'tags', []))
        return map(lambda tag: tag[u't'], tags)

    def add_tags(self, tags, user=None, perms=None):
        """添加用户标签"""
        allow, deny, grant = self.user_perms(user=user, perms=perms)
        if allow & M_TWRITE == 0:
            raise FuseOSError(EPERM)
        new_tags = self.underlying.get(u'tags', []).copy()
        sid = user.sid
        exists_tags = []
        for tag in new_tags:
            if tag[u't'] in tags:
                exists_tags.append(tag[u't'])
                if sid not in tag[u'u']:
                    tag[u'u'].append(sid)
        for tag in tags:
            if tag not in exists_tags:
                new_tags.append({u't': tag, u'u': [sid]})
        self.underlying[u'tags'] = new_tags
        self.changes[u'inodes'].add(u'tags')

    def remove_tags(self, tags, user=None, perms=None, manage=False):
        """删除标签"""
        allow, deny, grant = self.user_perms(user=user, perms=perms)
        if allow & M_TWRITE == 0:
            raise FuseOSError(EPERM)
        new_tags = self.underlying.get(u'tags', []).copy()
        sid = user.sid
        for tag in new_tags:
            if tag[u't'] in tags:
                if sid not in tag[u'u']:
                    tag[u'u'].remove(sid)
        new_tags = filter(lambda tag: len(tag[u'u']) > 0, new_tags)
        if manage and grant & M_TWRITE > 0:
            new_tags = filter(lambda tag: tag[u't'] not in tags, new_tags)
        self.underlying[u'tags'] = new_tags
        self.changes[u'inodes'].add(u'tags')

    def get_tags(self, result=None):
        """获取文件标签"""
        if result is None:
            result = {}
        result.update({u'tags': self.tags})
        return result

    def get_user_tags(self, result=None, user=None):
        """获取用户标签"""
        if result is None:
            result = {}
        result.update({u'utags': self.user_tags(user=user)})
        return result

    def record_tags(self):
        """记录文件标签到临时文件夹"""
        self.result = self.get_tags(result=self.result)
        return self

    def record_user_tags(self, user=None):
        """记录用户标签到临时结果"""
        self.result = self.get_user_tags(result=self.result, user=user)
        return self
