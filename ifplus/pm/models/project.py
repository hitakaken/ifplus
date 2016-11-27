# -*- coding: utf-8 -*-
from ifplus.res.models.file import FileObject


class Project(FileObject):
    def __init__(self, project_path, **kwargs):
        super(Project, self).__init__(project_path, **kwargs)
        self.props = None

    def load(self):
        self.props = self.underlying[u'project']




