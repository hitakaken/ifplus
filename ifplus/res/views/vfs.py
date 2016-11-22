# -*- coding: utf-8 -*-
import re
import urllib
from errno import *
from flask import current_app as app, Blueprint
from flask_login import current_user
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
file_object_model = FileObject.model(ns, file_meta_model, file_content_model)
# 操作请求/响应 Schemas
fs_action_response_model = Operations.fs_action_response_model(ns)
access_request_model = Operations.access_request_model(ns)
mkdir_request_model = Operations.mkdir_request_model(ns)
upload_model = Operations.upload_model(ns)
acl_request_model = Operations.acl_request_model(ns)
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
        kwargs = {'user': current_user, }
        return {}


@ns.route('/chmod/<path:file_path>')
class ChmodAction(Resource):
    @ns.expect(auth_token_model)
    @ns.doc(id='chmod')
    @ns.marshal_with(fs_action_response_model)
    def get(self, file_path):
        file_path = normalize_file_path(file_path)
        kwargs = {'user': current_user, }
        return {}


@ns.route('/chown/<path:file_path>')
class ChownAction(Resource):
    @ns.expect(auth_token_model)
    @ns.doc(id='chown')
    @ns.marshal_with(fs_action_response_model)
    def get(self, file_path):
        file_path = normalize_file_path(file_path)
        kwargs = {'user': current_user, }
        return {}


@ns.route('/facl/<path:file_path>')
class FaclAction(Resource):
    @ns.expect(auth_token_model)
    @ns.doc(id='getfacl')
    @ns.marshal_with(file_acl_model)
    def get(self, file_path):
        file_path = normalize_file_path(file_path)
        kwargs = {'user': current_user}
        return app.fs.getfacl(file_path, **kwargs).as_dict()

    @ns.expect(auth_token_model, acl_request_model)
    @ns.doc(id='addfacl')
    @ns.marshal_with(file_acl_model)
    def post(self, file_path):
        file_path = normalize_file_path(file_path)
        args = acl_request_model.parse_args()
        kwags = {'user': current_user, 'action': 1, 'scan': args['scan'] is not None and args['scan']}
        return app.fs.setfacl(file_path, args[u'ace'], **kwags).as_dict()

    @ns.expect(auth_token_model, acl_request_model)
    @ns.doc(id='setfacl')
    @ns.marshal_with(file_acl_model)
    def put(self, file_path):
        file_path = normalize_file_path(file_path)
        args = acl_request_model.parse_args()
        kwags = {'user': current_user, 'action': 0, 'scan': args['scan'] is not None and args['scan']}
        return app.fs.setfacl(file_path, args[u'ace'], **kwags).as_dict()

    @ns.expect(auth_token_model, acl_request_model)
    @ns.doc(id='delfacl')
    @ns.marshal_with(file_acl_model)
    def delete(self, file_path):
        file_path = normalize_file_path(file_path)
        args = acl_request_model.parse_args()
        kwags = {'user': current_user, 'action': -1, 'scan': args['scan'] is not None and args['scan']}
        return app.fs.setfacl(file_path, args[u'ace'], **kwags).as_dict()


@ns.route('/file/<path:file_path>')
class FileAction(Resource):
    @ns.expect(auth_token_model)
    @ns.doc(id='read')
    def get(self, file_path):
        kwargs = {'user': current_user, }
        file_path = normalize_file_path(file_path)
        resp, file_node = app.fs.open(file_path, None, **kwargs)
        # return file_node.underlying
        file_name = urllib.quote(file_node.underlying[u'name'].encode('utf8'))
        resp.headers['Content-Disposition'] = 'attachment; filename=%s' % file_name
        return resp

    @ns.expect(auth_token_model, upload_model)
    @ns.doc(id='write')
    @ns.marshal_with(file_meta_model)
    def put(self, file_path):
        file_path = normalize_file_path(file_path)
        args = upload_model.parse_args()
        kwargs = {'user': current_user, }
        mode = args['mod'] if args['mod'] is not None else '750'
        if mode_pattern.match(mode):
            mode = int(mode, 8)
        else:
            raise FuseOSError(EINVAL, http_status=400)
        kwargs['mode'] = mode
        if args['usr'] is not None:
            kwargs['owner'] = args['usr']
        if args['grp'] is not None:
            kwargs['group'] = args['grp']
        if args['fce'] is not None:
            kwargs['force'] = args['fce']
        if args['ovw'] is not None:
            kwargs['overwrite'] = args['ovw']
        upload_file = args['file']
        return app.fs.write(file_path, upload_file, 0, 0, **kwargs).meta().as_dict()

    @ns.expect(auth_token_model)
    @ns.doc(id='del')
    def delete(self, file_path):
        file_path = normalize_file_path(file_path)
        kwargs = {'user': current_user, }
        return {}


@ns.route('/folder/<path:file_path>')
class FolderActions(Resource):
    @ns.expect(auth_token_model)
    @ns.doc(id='ls')
    @ns.marshal_list_with(file_meta_model)
    def get(self, file_path):
        file_path = normalize_file_path(file_path)
        kwargs = {'user': current_user, }
        file_nodes = app.fs.readdir(file_path, 0, **kwargs)
        return [file_node.meta().as_dict() for file_node in file_nodes]

    @ns.expect(auth_token_model, mkdir_request_model)
    @ns.doc(id='mkdir')
    @ns.marshal_with(file_meta_model)
    def put(self, file_path):
        file_path = normalize_file_path(file_path)
        args = mkdir_request_model.parse_args()
        kwargs = {'user': current_user, }
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

    @ns.expect(auth_token_model, mkdir_request_model, upload_model)
    @ns.doc(id='mkdir')
    @ns.marshal_with(file_meta_model)
    def post(self, file_path):
        args = upload_model.parse_args()
        kwargs = {'user': current_user, }
        mode = args['mod'] if args['mod'] is not None else '750'
        if mode_pattern.match(mode):
            mode = int(mode, 8)
        else:
            raise FuseOSError(EINVAL, http_status=400)
        kwargs['mode'] = mode
        if args['usr'] is not None:
            kwargs['owner'] = args['usr']
        if args['grp'] is not None:
            kwargs['group'] = args['grp']
        if args['fce'] is not None:
            kwargs['force'] = args['fce']
        if args['ovw'] is not None:
            kwargs['overwrite'] = args['ovw']
        upload_file = args['file']
        file_path = normalize_file_path(file_path + '/' + upload_file.filename)
        return app.fs.write(file_path, upload_file, 0, 0, **kwargs).meta().as_dict()

    @ns.expect(auth_token_model)
    @ns.doc(id='rmdir')
    def delete(self, file_path):
        file_path = normalize_file_path(file_path)
        return {}


@ns.route('/move/<path:file_path>')
class MoveAction(Resource):
    @ns.expect(auth_token_model)
    @ns.doc(id='move')
    @ns.marshal_with(file_meta_model)
    def get(self, file_path):
        file_path = normalize_file_path(file_path)
        kwargs = {'user': current_user, }
        return app.fs.statfs(file_path, **kwargs).meta().as_dict()


@ns.route('/stat/<path:file_path>')
class StatfsAction(Resource):
    @ns.expect(auth_token_model)
    @ns.doc(id='stat')
    @ns.marshal_with(file_meta_model)
    def get(self, file_path):
        file_path = normalize_file_path(file_path)
        kwargs = {'user': current_user, }
        return app.fs.statfs(file_path, **kwargs).meta().as_dict()


@ns.route('/xattrs/<path:file_path>')
class XattrsActions(Resource):
    @ns.expect(auth_token_model)
    @ns.doc(id='getxattr')
    def get(self, file_path):
        file_path = normalize_file_path(file_path)
        kwargs = {'user': current_user, }
        return {}

    @ns.expect(auth_token_model)
    @ns.doc(id='setxattr')
    def post(self, file_path):
        file_path = normalize_file_path(file_path)
        kwargs = {'user': current_user, }
        return {}

    @ns.doc(id='removexattr')
    def delete(self, file_path):
        file_path = normalize_file_path(file_path)
        kwargs = {'user': current_user, }
        return {}

vfs_bp = Blueprint('vfs_bp', __name__, url_prefix='/raw')


@vfs_bp.route('/file/<path:file_path>')
def get_raw_file(file_path):
    kwargs = {'user': current_user, }
    file_path = normalize_file_path(file_path)
    resp, file_node = app.fs.open(file_path, None, **kwargs)
    resp.headers['Content-Type'] = 'application/octet-stream'
    file_name = urllib.quote(file_node.underlying[u'name'].encode('utf8'))
    resp.headers['Content-Disposition'] = 'attachment; filename=%s' % file_name
    return resp
