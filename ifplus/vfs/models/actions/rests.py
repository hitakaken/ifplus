# -*- coding: utf-8 -*-
from werkzeug.datastructures import FileStorage
from ifplus.restful.patched import fields


class Models(object):
    """Restful基本模型"""

    def __init__(self, ns):
        self.ns = ns
        self.errno = ns.model(u'VFSErrno', {
            u'errno': fields.Integer(title=u'错误码', description=u'错误码', required=True),
            u'message': fields.String(title=u'错误信息', description=u'错误信息')
        })
        self.ace = ns.model(u'FileACLEntry', {
            u'sid': fields.String(
                title=u'用户SID',
                description=u'ACL条目用户SID，SID由用户对象类型和用户对象ID组合而成，形如[u|g|r]:<UUID>，不能为空',
                required=True),
            u'perms': fields.List(
                fields.List(fields.Integer, min_items=3, max_items=3),
                title=u'用户权限',
                required=True, min_items=8, max_items=8),
            u'inherit': fields.Integer(title=u'可继承', description=u'0 代表不可继承, 1 代表可继承'),
        })
        self.hits = ns.model(u'FileHits', {
                u'o': fields.Integer(title=u'所有者点击', description=u'文件所有者访问文件内容的次数'),
                u'g': fields.Integer(title=u'所有组点击', description=u'文件所有组访问文件内容的次数'),
                u'u': fields.Integer(title=u'责任者点击', description=u'文件责任者(具有写权限)访问文件内容的次数'),
                u'p': fields.Integer(title=u'公众访问数', description=u'其他用户访问文件内容的次数'),
            }, title=u'点击数')
        self.inode = ns.model(u'FileINode', {
            u'fid': fields.String(title=u'唯一标识', required=True),
            u'dev': fields.String(title=u'所在设备', required=True),
            u'name': fields.String(title=u'文件名', required=True),
            u'owner': fields.String(title=u'所有者', required=True),
            u'group': fields.String(title=u'所在组', required=True),
            u'ftype': fields.String(title=u'文件类型', required=True),
            u'mode': fields.List(
                fields.List(fields.Integer, min_items=3, max_items=3),
                title=u'基本权限模式', min_items=3, max_items=3),
            u'nlink': fields.Integer(title=u'链接数', required=True),
            u'size': fields.Integer(title=u'文件大小', required=True),
            u'access': fields.DateTime(title=u'最后访问时间', required=True),
            u'modify': fields.DateTime(title=u'最后修改时间', description=u'上一次文件内容变动的时间', required=True),
            u'change': fields.DateTime(title=u'最后变更时间', description=u'上一次文件信息变动的时间', required=True),
            u'create': fields.DateTime(title=u'创建时间', required=True),
            u'creator': fields.String(title=u'创建者', required=True),
            u'perms': fields.List(
                fields.List(fields.Integer, min_items=3, max_items=3),
                title=u'用户权限',
                required=True, min_items=8, max_items=8),
            u'acl': fields.List(fields.Nested(self.ace), title=u'ACL权限列表'),
            u'hits': fields.Nested(self.hits),
            u'tags': fields.List(fields.String, title=u'文件标签'),
            u'xattrs': fields.Nested({}, additionalProperties=True),
            u'content': fields.String(title=u'文件内容'),
        })

CREATE_OPS = [u'mkdir', u'mkdirs', u'mkdirp', u'touch', u'link']
READ_OPS = [u'list', u'stat', u'download']
UPDATE_OPS = [u'write', u'rename', u'move', u'update']
DELETE_OPS = [u'rmdir', u'rm']


class Requests(object):
    """Restful请求参数"""

    def __init__(self, ns, models):
        self.ns = ns
        self.models = models
        self.update_model = ns.model(u'FileUpdateModel', {
            u'owner': fields.String(title=u'文件所有者'),
            u'group': fields.String(title=u'文件所有组'),
            u'mode': fields.List(
                fields.List(fields.Integer, min_items=3, max_items=3),
                title=u'基本权限模式', min_items=3, max_items=3),
            u'acl': fields.List(fields.Nested(models.ace), title=u'ACL权限列表'),
            u'content': fields.String(title=u'文件内容'),
            u'tags': fields.List(fields.String, title=u'文件标签'),
        })
        # 创建文件对象请求
        self.create = ns.parser()
        self.create.add_argument(u'op', help=u'操作类型', required=True, location=u'args')
        self.create.add_argument(u'returns', help=u'返回内容', action=u'append', location=u'args')
        # self.create.add_argument(u'file', help=u'上传文件', type=FileStorage, location=u'files')
        # op=mkdir
        # op=mkdirs
        self.create.add_argument(u'subdir', help=u'子文件夹名', action=u'append', location=u'args')
        # op=touch
        # op=link
        self.create.add_argument(u'target', help=u'目标文件', location=u'args')

        # 读取文件对象请求
        self.read = ns.parser()
        self.read.add_argument(u'op', help=u'操作类型', required=True, location=u'args')
        self.read.add_argument(u'returns', help=u'返回内容', action=u'append', location=u'args')
        # op=list
        self.read.add_argument(u'selfmode', help=u'是否返回本身', type=int, location=u'args')
        self.read.add_argument(u'recursion', help=u'是否递归', type=int, location=u'args')
        self.read.add_argument(u'withlinks', help=u'是否跟随链接', type=int, location=u'args')
        self.read.add_argument(u'page.size', help=u'每页记录数', type=int, location=u'args')
        self.read.add_argument(u'page.page', help=u'当前页码', type=int, location=u'args')
        # op=stat

        # op=list or stat

        # op=download

        # 更新文件对象请求
        self.update = ns.parser()
        self.update.add_argument(u'op', help=u'操作类型', required=True, location=u'args')
        self.update.add_argument(u'returns', help=u'返回内容', action=u'append', location=u'args')
        # op=update

        # op=rename

        # op=move



        # 删除文件对象请求
        self.delete = ns.parser()
        self.delete.add_argument(u'op', help=u'操作类型', required=True, location=u'args')
        # op=rmdir

        # op=rm

        # unlink

        # 上传文件对象
        self.upload = ns.parser()
        self.upload.add_argument(u'file', help=u'上传文件', type=FileStorage, required=True, location=u'files')

class Responses(object):
    """Restful请求响应"""

    def __init__(self, ns, models):
        self.ns = ns
        self.models = models
