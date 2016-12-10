# -*- coding: utf-8 -*-
# https://github.com/Voronenko/Storing_TreeView_Structures_WithMongoDB
from .actions import FileHits, FileXattrs, FileContent, FileComments, FileTags, FileTreeNode, FileShares


class FileObject(FileHits, FileXattrs, FileContent, FileComments, FileTags, FileTreeNode, FileShares):
    def __init__(self, file_path, underlying, vfs=None):
        super(FileObject, self).__init__(underlying, vfs=vfs)
        self.file_path = file_path

    @property
    def is_loaded(self):
        return self.underlying is None

    def load(self):
        if self.underlying is None and self.vfs is not None:
            self.underlying = self.vfs.load(self.file_path)