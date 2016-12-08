# -*- coding: utf-8 -*-
import stat
import os.path
from ifplus.restful.patched import fields


def model(ns):
    """File INode Swagger Model"""
    return ns.model('FileINode', {
            'name': fields.String(title='文件名', description='文件名', required=True),
            'fid': fields.String(title='唯一标识', required=True),
            'mode': fields.String(title='文件模式', required=True),
            'dev': fields.String(title='所在设备'),
            'nlink': fields.Integer(title='链接数', required=True),
            'owner': fields.String(title='所有者'),
            'group': fields.String(title='所在组'),
            'size': fields.Integer(title='文件大小', required=True),
            'access': fields.DateTime(title='最后访问时间', required=True),
            'modify': fields.DateTime(title='最后修改时间', description='上一次文件内容变动的时间', required=True),
            'change': fields.DateTime(title='最后变更时间', description='上一次文件信息变动的时间', required=True),
            'create': fields.DateTime(title='创建时间'),
            'creator': fields.String(title='创建者'),
            'perms': fields.String(title='访问者权限'),
            'hits': fields.Nested({
                'o': fields.Integer(title='所有者访问数'),
                'g': fields.Integer(title='所有者访问数'),
                'u': fields.Integer(title='用户访问数'),
                'p': fields.Integer(title='公众访问数'),
            }, title='点击数'),
        })


class FileINodeUtils(object):
    """文件 INode 工具类"""
    @staticmethod
    def file_id(file_object):
        """文件唯一标识"""
        return str(file_object.underlying['_id'])

    @staticmethod
    def name(file_object):
        """文件名"""
        return file_object.underlying['name']

    @staticmethod
    def splitext(file_object):
        """文件名分隔"""
        prefix, suffix = os.path.splitext(file_object.underlying['name'])
        return prefix, suffix

    @staticmethod
    def ext_name(file_object):
        """文件扩展名"""
        prefix, suffix = FileINodeUtils.splitext(file_object)
        return suffix

    @staticmethod
    def ancestors(file_object):
        """祖先节点"""
        return file_object.fs.devices[file_object.underlying['dev']].mountpoint + file_object.underlying['ancestors']

    @staticmethod
    def is_file(file_object):
        """是否普通文件"""
        return stat.S_ISREG(file_object.underlying['mode'])

    @staticmethod
    def is_folder(file_object):
        """是否目录文件"""
        return stat.S_ISDIR(file_object.underlying['mode'])

    @staticmethod
    def is_link(file_object):
        """是否符号链接"""
        return stat.S_ISLNK(file_object.underlying['mode'])

    @staticmethod
    def is_block_special(file_object):
        """是否块设备"""
        return stat.S_ISBLK(file_object.underlying['mode'])

    @staticmethod
    def is_character_special(file_object):
        """是否字符设备"""
        return stat.S_ISCHR(file_object.underlying['mode'])

    @staticmethod
    def is_fifo(file_object):
        """是否命名管道"""
        return stat.S_ISFIFO(file_object.underlying['mode'])

    @staticmethod
    def is_socket(file_object):
        """是否套接字"""
        return stat.S_ISSOCK(file_object.underlying['mode'])

