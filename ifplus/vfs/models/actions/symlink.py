# -*- coding: utf-8 -*-
from errno import EPERM
from ..exceptions import FuseOSError
from .acls import FileAcls, M_WRITE


class FileSymlink(FileAcls):
    """文件软链接工具类"""
    def __init__(self, underlying, vfs=None):
        super(FileSymlink, self).__init__(underlying, vfs=vfs)

    def init_symlink(self, target):
        """初始化软链接"""
        self.underlying[u'mode'] &= 0x80000000 | 0o007777
        self.underlying[u'mode'] |= 0o120000
        self.underlying[u'symlink'] = {
            u'id': target.fid,
            u'path': target.real_path,
            u'type': (u'%06o' % (0o0177777 & target.mode))[:2],
        }
        target.add_link(self)
        return self

    @property
    def symlink(self):
        return self.underlying[u'symlink'] if self.is_link else None

    @symlink.setter
    def symlink(self, target):
        if target is not None:
            self.underlying[u'mode'] &= 0x80000000 | 0o007777
            self.underlying[u'mode'] |= 0o120000
            self.underlying[u'symlink'] = target
            self.changes[u'inodes'].add(u'mode')
            self.changes[u'inodes'].add(u'symlink')
        else:
            self.underlying[u'mode'] &= 0x80000000 | 0o007777
            self.underlying[u'mode'] |= 0o100000
            self.underlying[u'symlink'] = None
            self.changes[u'inodes'].add(u'mode')
            self.changes[u'inodes'].add(u'symlink')

    def change_symlink(self, target, user=None, perms=None):
        allow, deny, grant = self.user_perms(user=user, perms=perms)
        if allow & M_WRITE == 0:
            raise FuseOSError(EPERM)
        self.symlink = {
            u'id': target.fid,
            u'path': target.real_path,
            u'type': (u'%06o' % (0o0177777 & target.mode))[:2],
        }

    def get_symlink(self, result=None):
        """记录文件软链接"""
        if result is None:
            result = {}
        if self.is_link:
            result.update({u'symlink': self.symlink})
        return result

    def record_symlink(self):
        self.result = self.get_symlink(result=self.result)
        return self

    @property
    def links(self):
        return self.underlying.get(u'links', [])

    def add_link(self, link):
        found = False
        new_links = []
        for link_file in self.links:
            if link_file[u'id'] == link.fid:
                found = True
                new_links.append({u'id': link.fid, u'path': link.real_path})
            else:
                new_links.append(link_file)
        if not found:
            new_links.append({u'id': link.fid, u'path': link.real_path})
            self.nlink = len(new_links) + 1
        self.underlying[u'links'] = new_links
        self.changes[u'inodes'].add(u'links')

    def remove_link(self, link):
        found = False
        new_links = []
        for link_file in self.links:
            if link_file[u'id'] == link.fid:
                found = True
            else:
                new_links.append(link_file)
        if found:
            self.nlink = len(new_links) + 1
            self.underlying[u'links'] = new_links
            self.changes[u'inodes'].add(u'links')
