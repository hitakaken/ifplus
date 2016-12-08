# -*- coding: utf-8 -*-
from ifplus.restful.patched import fields

FILE_INODE = {
    u'fid': fields.String(title=u'唯一标识', required=True),
    u'dev': fields.String(title=u'所在设备', required=True),
    u'name': fields.String(title=u'文件名', required=True),
    u'owner': fields.String(title=u'所有者', required=True),
    u'group': fields.String(title=u'所在组', required=True),
    u'mode': fields.String(title=u'文件模式', required=True),
    u'nlink': fields.Integer(title=u'链接数', required=True),
    u'size': fields.Integer(title=u'文件大小', required=True),
    u'access': fields.DateTime(title=u'最后访问时间', required=True),
    u'modify': fields.DateTime(title=u'最后修改时间', description=u'上一次文件内容变动的时间', required=True),
    u'change': fields.DateTime(title=u'最后变更时间', description=u'上一次文件信息变动的时间', required=True),
    u'create': fields.DateTime(title=u'创建时间', required=True),
    u'creator': fields.String(title=u'创建者', required=True),
}

FILE_ACE = {
    u'sid': fields.String(
        title=u'用户SID',
        description=u'ACL条目用户SID，SID由用户对象类型和用户对象ID组合而成，形如[u|g|r]:<UUID>，不能为空',
        required=True),
    u'mask': fields.List(
        fields.Integer,
        title=u'用户权限',
        description=u'',
        required=True, min_items=26, max_items=26)
}


def model(ns):
    """File INode Swagger Model"""
    return ns.model('FileINode', {
        'fid': fields.String(title='唯一标识', required=True),
        'dev': fields.String(title='所在设备', required=True),
        'name': fields.String(title='文件名', description='文件名', required=True),
        'owner': fields.String(title='所有者', required=True),
        'group': fields.String(title='所在组', required=True),
        'mode': fields.String(title='文件模式', required=True),
        'nlink': fields.Integer(title='链接数', required=True),
        'size': fields.Integer(title='文件大小', required=True),
        'access': fields.DateTime(title='最后访问时间', required=True),
        'modify': fields.DateTime(title='最后修改时间', description='上一次文件内容变动的时间', required=True),
        'change': fields.DateTime(title='最后变更时间', description='上一次文件信息变动的时间', required=True),
        'create': fields.DateTime(title='创建时间', required=True),
        'creator': fields.String(title='创建者', required=True),
        'perms': fields.List(fields.Boolean, title='访问者权限'),
        'hits': fields.Nested({
            'o': fields.Integer(title='所有者访问数'),
            'g': fields.Integer(title='所有者访问数'),
            'u': fields.Integer(title='用户访问数'),
            'p': fields.Integer(title='公众访问数'),
        }, title='点击数'),
    })
