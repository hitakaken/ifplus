# -*- coding: utf-8 -*-
from .xattrs import FileXattrs


class Project(FileXattrs):
    def __init__(self, underlying, vfs=None):
        super(Project, self).__init__(underlying, vfs=vfs)

    def make_as_project(self):
        if u'project' in self.underlying:
            self.underlying[u'project'] = {
                u'filed': False,
                u'business': []
            }
