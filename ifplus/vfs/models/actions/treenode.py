# -*- coding: utf-8 -*-
from .symlink import FileSymlink


class FileTreeNode(FileSymlink):
    """文件树工具类"""
    def __init__(self, underlying, vfs=None):
        super(FileTreeNode, self).__init__(underlying, vfs=vfs)

    def init_tree(self, parent=None, ancestors=None):
        """初始化文件树"""
        if self.underlying[u'parent'] is None:
            self.underlying[u'parent'] = parent
        if self.underlying[u'ancestors'] is None:
            if ancestors is None:
                if parent is None:
                    ancestors = []
                else:
                    ancestors = self.vfs.lookup(parent).pathnames
            self.underlying[u'ancestors'] = ancestors
        return self

    @property
    def ancestors(self):
        """文件祖先节点"""
        return self.underlying[u'ancestors']

    @property
    def parent(self):
        """文件父节点ID"""
        return self.underlying[u'parent']

    @property
    def parent_file(self):
        """父节点文件对象"""
        return self.vfs.root_file if self.parent is None else self.vfs.lookup(self.parent)

    @property
    def real_path(self):
        """文件真实路径，跟随软链接"""
        return u'/'.join(self.ancestors) + u'/' + self.name

    def get_real_path(self, result=None):
        """获取文件真实路径"""
        if result is None:
            result = {}
        result.update({
            u'path': self.real_path
        })
        return result

    def record_real_path(self):
        """记录文件真实路径到临时结果"""
        self.result = self.get_real_path(result=self.result)
        return self