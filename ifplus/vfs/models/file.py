# -*- coding: utf-8 -*-
# https://github.com/Voronenko/Storing_TreeView_Structures_WithMongoDB
import datetime

from ifplus.vfs.models.actions import CONTENT_TYPE_UNKNOWN
from ifplus.vfs.models.actions import STORAGE_UNKNOWN
from .actions import FileHits, FileContent, FileComments, FileTags, FileTreeNode, FileShares, FileProject


class FileObject(FileHits, FileProject, FileContent, FileComments, FileTags, FileTreeNode, FileShares):
    def __init__(self, file_path, underlying, vfs=None):
        super(FileObject, self).__init__(underlying, vfs=vfs)
        self.file_path = file_path
        self.is_newly = False
        self.content = None

    def init(self, parent_file, name, time=None, user=None, is_file=False, target_file=None):
        self.is_newly = True
        if time is None:
            time = datetime.datetime.utcnow()
        self.init_inode(name, time, user=user)
        self.mode = parent_file.mode
        self.init_acl(parent_file.inherits)
        self.init_hits()
        self.init_xattrs()
        self.init_tags()
        self.init_comments(parent_file.is_comments_enabled)
        self.init_tree(
            parent=parent_file.id,
            ancestors=[] if parent_file.id is None else parent_file.ancestors + [parent_file.name])
        self.init_content(STORAGE_UNKNOWN, CONTENT_TYPE_UNKNOWN)
        if is_file:
            self.underlying[u'mode'] &= 0x80000000 | 0o007777
            self.underlying[u'mode'] |= 0o100000
        if target_file is not None:
            self.init_symlink(target_file)

    @property
    def is_loaded(self):
        return self.underlying is None

    def load(self):
        if self.underlying is None and self.vfs is not None:
            self.underlying = self.vfs.load(self.file_path)