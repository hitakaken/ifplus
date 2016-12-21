# -*- coding: utf-8 -*-
from .xattrs import FileXattrs


class FileProject(FileXattrs):
    def __init__(self, underlying, vfs=None):
        super(FileProject, self).__init__(underlying, vfs=vfs)

    def make_as_project(self):
        if u'project' not in self.underlying:
            self.underlying[u'project'] = {
                u'filed': False
            }

    @property
    def is_project(self):
        return u'project' in self.underlying

    @property
    def is_filed(self):
        return u'project' in self.underlying and self.underlying[u'project'][u'filed']

    @is_filed.setter
    def is_filed(self, filed):
        if  u'project' in self.underlying or filed:
            self.underlying[u'project'] = {
                u'filed': filed
            }
            self.changes[u'inodes'].add(u'project')