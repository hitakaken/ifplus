# -*- coding: utf-8 -*-
from .symlink import FileSymlink


class FileTreeNode(FileSymlink):
    """文件树工具类"""
    def __init__(self, underlying, vfs=None):
        super(FileTreeNode, self).__init__(underlying, vfs=vfs)

    def init_tree(self, parent=None, ancestors=None):
        """初始化文件树"""
        if u'parent'not in self.underlying:
            self.underlying[u'parent'] = parent
        if u'ancestors' not in self.underlying:
            if ancestors is None:
                if parent is None:
                    ancestors = []
                else:
                    ancestors = self.vfs.lookup(parent).pathnames
            self.underlying[u'ancestors'] = ancestors
        return self

    # @property
    # def ancestors(self):
    #     """文件祖先节点"""
    #     return self.underlying.get(u'ancestors', [])

    @property
    def parent(self):
        """文件父节点ID"""
        return self.underlying.get(u'parent', None)

    @property
    def parent_file(self):
        """父节点文件对象"""
        return self.vfs.root_file if self.parent is None else self.vfs.lookup(self.parent)

    @property
    def real_path(self):
        """文件真实路径，跟随软链接"""
        real_path = u'/'.join(self.ancestors) + u'/' + self.name
        if real_path[0] != u'/':
            real_path = u'/' + real_path
        return real_path

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

    @property
    def partnames(self):
        return self.ancestors + [self.name]
