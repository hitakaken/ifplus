# -*- coding: utf-8 -*-
import re
import urllib
from errno import *
from flask import current_app as app, Blueprint
from flask_login import current_user, login_required
from ifplus.restful.patched import Namespace, Resource
from ifplus.restful.datatypes import BOOLEAN_VALUE
# from ifplus.auth.models.token import UserToken
from ..models.exceptions import FuseOSError
from ..models.actions.rests import Models, Requests, Responses
from ..models.file import *

ns = Namespace('fs',
               title='文件管理API',
               version='1.0',
               description='文件管理 RESTful API',
               tags='files')

models = Models(ns)
requests = Requests(ns, models)
responses = Responses(ns, models)


@ns.errorhandler(FuseOSError)
@ns.marshal_with(models.errno, code=500, description='文件系统错误')
def handle_fuse_os_error(error):
    """File System Responses With Errno code"""
    resp = {
        'errno': error.errno,
        'message': str(error)
    }
    return resp, error.http_status

# 认证 Schema
# auth_token_model = UserToken.model(ns)
# 文件对象 Schemas
# file_meta_model = FileMetaInfo.model(ns)
# file_content_model = FileContent.model(ns)
# file_xattrs_model = FileExtraAttributes.model(ns)
# file_acl_model = FileAccessControlList.model(ns)
# file_node_model = FileTreeNode.model(ns)
# file_object_model = FileObject.model(ns, file_meta_model, file_content_model)
# 操作请求/响应 Schemas
# fs_action_response_model = Operations.fs_action_response_model(ns)
# fs_requests = Operations.requests(ns)
# 正则校验表达式 Patterns
# mode_pattern = re.compile('^[0-7]{3}$')


@ns.route('/files/')
class UserRootView(Resource):
    @ns.doc(id='enter')
    @login_required
    def get(self):
        for role in app.tokens.supers:
            current_user.roles.append(role)
        kwargs = {
            u'user': current_user,
            u'returns': [u'path', u'inodes', u'hits'],
            u'op': u'stat'
        }
        result = app.vfs.read(u'/', **kwargs)
        result[u'children'] = [
            app.vfs.read('~', **kwargs),
            app.vfs.read(u'projects', **kwargs),
            # app.vfs.read(u'Market', **kwargs)
        ]
        return result


@ns.route('/files/<path:file_path>')
class Files(Resource):
    @ns.doc(id='create')
    @ns.expect(requests.create, requests.update_model)
    @login_required
    def post(self, file_path):
        kwargs = {u'user': current_user}
        kwargs.update(requests.create.parse_args())
        kwargs.update({u'payload': app.api.payload})
        return app.vfs.create(file_path, **kwargs)

    @ns.doc(id='read', produces=['application/json', 'application/octet-stream'])
    @ns.expect(requests.read)
    # @ns.response(code=404, model=models.errno, description='文件/文件夹不存在')
    def get(self, file_path):
        kwargs = {u'user': current_user}
        print current_user
        kwargs.update(requests.read.parse_args())
        return app.vfs.read(file_path, **kwargs)

    @ns.doc(id='update')
    @ns.expect(requests.update, requests.update_model)
    @login_required
    def put(self, file_path):
        kwargs = {u'user': current_user}
        kwargs.update(requests.update.parse_args())
        kwargs.update({u'payload': app.api.payload})
        return app.vfs.update(file_path, **kwargs)

    @ns.doc(id='delete')
    @ns.expect(requests.delete)
    @login_required
    def delete(self, file_path):
        kwargs = {u'user': current_user}
        kwargs.update(requests.delete.parse_args())
        kwargs.update({u'payload': app.api.payload})
        return app.vfs.delete(file_path, **kwargs)


@ns.route('/upload/<path:file_path>')
class Upload(Resource):
    @ns.doc(id='upload')
    @ns.expect(requests.upload)
    @login_required
    def post(self, file_path):
        kwargs = {u'user': current_user}
        kwargs.update(requests.upload.parse_args())
        return app.vfs.upload(file_path, **kwargs)


# # 通用处理
# # 路径处理
# def normalize_file_path(file_path, user=None):
#     if file_path.startswith('/'):
#         return file_path
#     if file_path.startswith('~/'):
#         prefix = user.account if user is not None else None
#         prefix = '/tmp' if prefix is None else '/home/' + prefix
#         return prefix + file_path[1:]
#     return '/' + file_path
#
#
# def copy_args_to_kwargs(args, kwargs):
#     mode = args['mod'] if args['mod'] is not None else '750'
#     if mode_pattern.match(mode):
#         mode = int(mode, 8)
#     else:
#         raise FuseOSError(EINVAL, http_status=400)
#     kwargs['mode'] = mode
#     if args['usr'] is not None:
#         kwargs['owner'] = args['usr']
#     if args['grp'] is not None:
#         kwargs['group'] = args['grp']
#     if args['fce'] is not None:
#         kwargs['force'] = args['fce']
#     if args['ovw'] is not None:
#         kwargs['overwrite'] = args['ovw']
#     return kwargs
#
#
# @ns.route('/access/<path:file_path>')
# class AccessAction(Resource):
#     @ns.expect(auth_token_model, fs_requests['access'])
#     @ns.doc(id='access')
#     @ns.marshal_with(BOOLEAN_VALUE)
#     def get(self, file_path):
#         file_path = normalize_file_path(file_path)
#         args = fs_requests['access'].parse_args()
#         kwargs = {'user': current_user, }
#         return {}
#
#
# @ns.route('/chmod/<path:file_path>')
# class ChmodAction(Resource):
#     @ns.expect(auth_token_model, fs_requests['chmod'])
#     @ns.doc(id='chmod')
#     @ns.marshal_with(fs_action_response_model)
#     def get(self, file_path):
#         file_path = normalize_file_path(file_path)
#         args = fs_requests['chmod'].parse_args()
#         kwargs = {'user': current_user, }
#         return {}
#
#
# @ns.route('/chown/<path:file_path>')
# class ChownAction(Resource):
#     @ns.expect(auth_token_model, fs_requests['chown'])
#     @ns.doc(id='chown')
#     @ns.marshal_with(fs_action_response_model)
#     def get(self, file_path):
#         file_path = normalize_file_path(file_path)
#         args = fs_requests['chown'].parse_args()
#         kwargs = {'user': current_user, }
#         app.fs.access(file_path, )
#         return {}
#
#
# @ns.route('/facl/<path:file_path>')
# class FaclAction(Resource):
#     @ns.expect(auth_token_model)
#     @ns.doc(id='getfacl')
#     @ns.marshal_with(file_acl_model)
#     def get(self, file_path):
#         file_path = normalize_file_path(file_path)
#         kwargs = {'user': current_user}
#         return app.fs.getfacl(file_path, **kwargs).as_dict()
#
#     @ns.expect(auth_token_model, fs_requests['acl'])
#     @ns.doc(id='addfacl')
#     @ns.marshal_with(file_acl_model)
#     def post(self, file_path):
#         file_path = normalize_file_path(file_path)
#         args = fs_requests['acl'].parse_args()
#         kwags = {'user': current_user, 'action': 1, 'scan': args['scan'] is not None and args['scan']}
#         return app.fs.setfacl(file_path, args[u'ace'], **kwags).as_dict()
#
#     @ns.expect(auth_token_model, fs_requests['acl'])
#     @ns.doc(id='setfacl')
#     @ns.marshal_with(file_acl_model)
#     def put(self, file_path):
#         file_path = normalize_file_path(file_path)
#         args = fs_requests['acl'].parse_args()
#         kwags = {'user': current_user, 'action': 0, 'scan': args['scan'] is not None and args['scan']}
#         return app.fs.setfacl(file_path, args[u'ace'], **kwags).as_dict()
#
#     @ns.expect(auth_token_model, fs_requests['acl'])
#     @ns.doc(id='delfacl')
#     @ns.marshal_with(file_acl_model)
#     def delete(self, file_path):
#         file_path = normalize_file_path(file_path)
#         args = fs_requests['acl'].parse_args()
#         kwags = {'user': current_user, 'action': -1, 'scan': args['scan'] is not None and args['scan']}
#         return app.fs.setfacl(file_path, args[u'ace'], **kwags).as_dict()
#
#
# @ns.route('/file/<path:file_path>')
# @ns.doc(params={'file_path': '文件路径'})
# class FileAction(Resource):
#     @ns.expect(auth_token_model)
#     @ns.doc(id='read')
#     def get(self, file_path):
#         kwargs = {'user': current_user, }
#         file_path = normalize_file_path(file_path)
#         resp, file_node = app.fs.open(file_path, None, **kwargs)
#         # return file_node.underlying
#         file_name = urllib.quote(file_node.underlying[u'name'].encode('utf8'))
#         resp.headers['Content-Disposition'] = 'attachment; filename=%s' % file_name
#         return resp
#
#     @ns.expect(auth_token_model, fs_requests['upload'])
#     @ns.doc(id='write')
#     @ns.marshal_with(file_meta_model)
#     def put(self, file_path):
#         file_path = normalize_file_path(file_path)
#         args = fs_requests['upload'].parse_args()
#         kwargs = {'user': current_user, }
#
#         upload_file = args['file']
#         return app.fs.write(file_path, upload_file, 0, 0, **kwargs).meta().as_dict()
#
#     @ns.expect(auth_token_model)
#     @ns.doc(id='del')
#     @ns.marshal_with(BOOLEAN_VALUE)
#     def delete(self, file_path):
#         file_path = normalize_file_path(file_path)
#         kwargs = {'user': current_user, }
#         return {}
#
#
# @ns.route('/folder/<path:file_path>')
# class FolderActions(Resource):
#     @ns.expect(auth_token_model)
#     @ns.doc(id='ls')
#     @ns.marshal_list_with(file_meta_model)
#     def get(self, file_path):
#         file_path = normalize_file_path(file_path)
#         kwargs = {'user': current_user, }
#         file_nodes = app.fs.readdir(file_path, 0, **kwargs)
#         return [file_node.meta().as_dict() for file_node in file_nodes]
#
#     @ns.expect(auth_token_model, fs_requests['mkdir'])
#     @ns.doc(id='mkdir')
#     @ns.marshal_with(file_meta_model)
#     def put(self, file_path):
#         file_path = normalize_file_path(file_path)
#         args = fs_requests['mkdir'].parse_args()
#         kwargs = {'user': current_user, }
#         mode = args['mod'] if args['mod'] is not None else '750'
#         if mode_pattern.match(mode):
#             mode = int(mode, 8)
#         else:
#             raise FuseOSError(EINVAL, http_status=400)
#         if args['usr'] is not None:
#             kwargs['owner'] = args['usr']
#         if args['grp'] is not None:
#             kwargs['group'] = args['grp']
#         if args['fce'] is not None:
#             kwargs['force'] = args['fce']
#         # kwargs['user] = current_user
#         return app.fs.mkdir(file_path, mode, **kwargs).meta().as_dict()
#
#     @ns.expect(auth_token_model, fs_requests['upload'])
#     @ns.doc(id='upload')
#     @ns.marshal_with(file_meta_model)
#     def post(self, file_path):
#         file_path = normalize_file_path(file_path + '/' + upload_file.filename)
#         args = fs_requests['upload'].parse_args()
#         kwargs = {'user': current_user, }
#         mode = args['mod'] if args['mod'] is not None else '750'
#         if mode_pattern.match(mode):
#             mode = int(mode, 8)
#         else:
#             raise FuseOSError(EINVAL, http_status=400)
#         kwargs['mode'] = mode
#         if args['usr'] is not None:
#             kwargs['owner'] = args['usr']
#         if args['grp'] is not None:
#             kwargs['group'] = args['grp']
#         if args['fce'] is not None:
#             kwargs['force'] = args['fce']
#         if args['ovw'] is not None:
#             kwargs['overwrite'] = args['ovw']
#         upload_file = args['file']
#
#         return app.fs.write(file_path, upload_file, 0, 0, **kwargs).meta().as_dict()
#
#     @ns.expect(auth_token_model)
#     @ns.doc(id='rmdir')
#     @ns.marshal_with(BOOLEAN_VALUE)
#     def delete(self, file_path):
#         file_path = normalize_file_path(file_path)
#         return {}
#
#
# @ns.route('/rename/<path:file_path>')
# class RenameAction(Resource):
#     @ns.expect(auth_token_model, fs_requests['rename'])
#     @ns.doc(id='rename')
#     @ns.marshal_with(file_meta_model)
#     def get(self, file_path):
#         file_path = normalize_file_path(file_path)
#         args = fs_requests['rename'].parse_args()
#         kwargs = {'user': current_user, }
#         return {}
#
#
# @ns.route('/stat/<path:file_path>')
# class StatfsAction(Resource):
#     @ns.expect(auth_token_model)
#     @ns.doc(id='stat')
#     @ns.marshal_with(file_meta_model)
#     def get(self, file_path):
#         file_path = normalize_file_path(file_path)
#         kwargs = {'user': current_user, }
#         return app.fs.statfs(file_path, **kwargs).meta().as_dict()
#
#
# @ns.route('/xattrs/<path:file_path>')
# class XattrsActions(Resource):
#     @ns.expect(auth_token_model, fs_requests['xattrs'])
#     @ns.doc(id='getxattr')
#     @ns.marshal_with(file_xattrs_model)
#     def get(self, file_path):
#         file_path = normalize_file_path(file_path)
#         args = fs_requests['xattrs'].parse_args()
#         kwargs = {'user': current_user, }
#         return {}
#
#     @ns.expect(auth_token_model, fs_requests['xattrs'])
#     @ns.doc(id='setxattr')
#     @ns.marshal_with(file_xattrs_model)
#     def post(self, file_path):
#         file_path = normalize_file_path(file_path)
#         args = fs_requests['xattrs'].parse_args()
#         kwargs = {'user': current_user, }
#         return {}
#
#     @ns.expect(auth_token_model, fs_requests['xattrs'])
#     @ns.doc(id='removexattr')
#     @ns.marshal_with(BOOLEAN_VALUE)
#     def delete(self, file_path):
#         file_path = normalize_file_path(file_path)
#         args = fs_requests['xattrs'].parse_args()
#         kwargs = {'user': current_user, }
#         return {}
#
# vfs_bp = Blueprint('vfs_bp', __name__, url_prefix='/raw')
#
#
# @vfs_bp.route('/file/<path:file_path>')
# def get_raw_file(file_path):
#     kwargs = {'user': current_user, }
#     file_path = normalize_file_path(file_path)
#     resp, file_node = app.fs.open(file_path, None, **kwargs)
#     resp.headers['Content-Type'] = 'application/octet-stream'
#     file_name = urllib.quote(file_node.underlying[u'name'].encode('utf8'))
#     resp.headers['Content-Disposition'] = 'attachment; filename=%s' % file_name
#     return resp
