# -*- coding: utf-8 -*-
from errno import EPERM
from ..exceptions import FuseOSError
from .acls import FileAcls


class FileComments(FileAcls):
    """文件评论工具类"""
    def __init__(self, underlying, vfs=None):
        super(FileComments, self).__init__(underlying, vfs=vfs)

    def init_comments(self, enabled=False):
        if u'comments' not in self.underlying:
            self.underlying[u'comments'] = {
                u'enabled': enabled
            }
        return self

    @property
    def is_comments_enabled(self):
        return self.underlying.get(u'comments', {}).get(u'enabled', False)

    def enable_comments(self, user=None, perms=None):
        if self.is_full_controller(user=user, perms=None):
            self.underlying[u'comments'][u'enabled'] = True
            self.changes[u'inodes'].add(u'comments')
        else:
            raise FuseOSError(EPERM)




