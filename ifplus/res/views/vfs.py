# -*- coding: utf-8 -*-
import re
from flask import current_app as app
from errno import *
from ifplus.restful.patched import Namespace, Resource
from ifplus.auth.models.token import UserToken
from ..base.operations import Operations, FuseOSError
from ..models.file import *

ns = Namespace('fs',
               title='文件管理API',
               version='1.0',
               description='文件管理 RESTful API',
               tags='files')

# 错误 Schema
errno_model = FuseOSError.model(ns)


@ns.errorhandler(FuseOSError)
@ns.marshal_with(errno_model, code=500, description='文件系统错误')
def handle_fuse_os_error(error):
    resp = {
        'errno': error.errno,
        'message': str(error)
    }
    return resp, error.http_status

# 认证 Schema
auth_token_model = UserToken.model(ns)
# 文件对象 Schemas
file_meta_model = FileMetaInfo.model(ns)
file_content_model = FileContent.model(ns)
file_xattrs_model = FileExtraAttributes.model(ns)
file_acl_model = FileAccessControlList.model(ns)
file_node_model = FileTreeNode.model(ns)
file_object_model = FileObject.model(ns,
                                     file_meta_model,
                                     file_content_model,
                                     file_acl_model,)
# 操作请求/响应 Schemas
fs_action_response_model = Operations.fs_action_response_model(ns)
access_request_model = Operations.access_request_model(ns)
mkdir_request_model = Operations.mkdir_request_model(ns)
upload_model = Operations.upload_model(ns)
# 正则校验表达式 Patterns
mode_pattern = re.compile('^[0-7]{3}$')


# 通用处理
# 路径处理
def normalize_file_path(file_path, user=None):
    if file_path.startswith('/'):
        return file_path
    if file_path.startswith('~/'):
        prefix = user.account if user is not None else None
        prefix = '/tmp' if prefix is None else '/home/' + prefix
        return prefix + file_path[1:]
    return '/' + file_path


@ns.route('/access/<path:file_path>')
class AccessAction(Resource):
    @ns.expect(auth_token_model, access_request_model)
    @ns.doc(id='access')
    @ns.marshal_with(fs_action_response_model)
    def get(self, file_path):
        file_path = normalize_file_path(file_path)
        print file_path
        return {}


@ns.route('/chmod/<path:file_path>')
class ChmodAction(Resource):
    @ns.expect(auth_token_model)
    @ns.doc(id='chmod')
    @ns.marshal_with(fs_action_response_model)
    def get(self, file_path):
        file_path = normalize_file_path(file_path)
        return {}


@ns.route('/chown/<path:file_path>')
class ChownAction(Resource):
    @ns.expect(auth_token_model)
    @ns.doc(id='chown')
    @ns.marshal_with(fs_action_response_model)
    def get(self, file_path):
        file_path = normalize_file_path(file_path)
        return {}


@ns.route('/facl/<path:file_path>')
class FaclAction(Resource):
    @ns.expect(auth_token_model)
    @ns.doc(id='getfacl')
    def get(self, file_path):
        file_path = normalize_file_path(file_path)
        return {}

    @ns.expect(auth_token_model)
    @ns.doc(id='setfacl')
    def post(self, file_path):
        file_path = normalize_file_path(file_path)
        return {}


@ns.route('/file/<path:file_path>')
class FileAction(Resource):
    @ns.expect(auth_token_model)
    @ns.doc(id='read')
    def get(self, file_path):
        file_path = normalize_file_path(file_path)
        return {}

    @ns.expect(auth_token_model, upload_model)
    @ns.doc(id='write')
    def post(self, file_path):
        file_path = normalize_file_path(file_path)
        return {}

    @ns.expect(auth_token_model)
    @ns.doc(id='del')
    def delete(self, file_path):
        file_path = normalize_file_path(file_path)
        return {}


@ns.route('/folder/<path:file_path>')
class FolderActions(Resource):
    @ns.expect(auth_token_model)
    @ns.doc(id='ls')
    def get(self, file_path):
        file_path = normalize_file_path(file_path)
        return {}

    @ns.expect(auth_token_model, mkdir_request_model)
    @ns.doc(id='mkdir')
    @ns.marshal_with(file_meta_model)
    def post(self, file_path):
        file_path = normalize_file_path(file_path)
        args = mkdir_request_model.parse_args()
        kwargs = {}
        mode = args['mod'] if args['mod'] is not None else '750'
        if mode_pattern.match(mode):
            mode = int(mode, 8)
        else:
            raise FuseOSError(EINVAL, http_status=400)
        if args['usr'] is not None:
            kwargs['owner'] = args['usr']
        if args['grp'] is not None:
            kwargs['group'] = args['grp']
        if args['fce'] is not None:
            kwargs['force'] = args['fce']
        # kwargs['user] = current_user
        return app.fs.mkdir(file_path, mode, **kwargs).meta().as_dict()

    @ns.expect(auth_token_model)
    @ns.doc(id='rmdir')
    def delete(self, file_path):
        file_path = normalize_file_path(file_path)
        return {}


@ns.route('/stat/<path:file_path>')
class StatfsAction(Resource):
    @ns.expect(auth_token_model)
    @ns.doc(id='stat')
    @ns.marshal_with(file_meta_model)
    def get(self, file_path):
        file_path = normalize_file_path(file_path)
        # print file_path
        return {}


@ns.route('/xattrs/<path:file_path>')
class XattrsActions(Resource):
    @ns.expect(auth_token_model)
    @ns.doc(id='getxattr')
    def get(self, file_path):
        file_path = normalize_file_path(file_path)
        return {}

    @ns.expect(auth_token_model)
    @ns.doc(id='setxattr')
    def post(self, file_path):
        file_path = normalize_file_path(file_path)
        return {}

    @ns.doc(id='removexattr')
    def delete(self, file_path):
        file_path = normalize_file_path(file_path)
        return {}

