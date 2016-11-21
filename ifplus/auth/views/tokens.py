# -*- coding: utf-8 -*-
from flask import current_app as app
from werkzeug.exceptions import NotFound, Unauthorized
from ifplus.restful.patched import Namespace, Resource, fields


ns = Namespace('auth',
               title='认证授权 API',
               version='1.0',
               description='认证授权 RESTful API',
               tags='tokens')

# 验证 Form
authenticate_request = ns.parser()
authenticate_request.add_argument('username', required=True, location='form')
authenticate_request.add_argument('password', required=True, location='form')
# 令牌 请求
token_request = ns.parser()
token_request.add_argument('token', location='form')
# 令牌 响应
token_response = ns.model('Token', {
    'token': fields.String
})


@ns.route('/authenticate')
class Authenticate(Resource):
    @ns.expect(authenticate_request)
    @ns.marshal_with(token_response)
    @ns.doc(id='authenticate')
    def post(self):
        """
        Authenticate

        :raises NotFound:  User not found
        :raises Unauthorized:  Authenticate Failed
        """
        args = authenticate_request.parse_args()
        user = app.rbac.users.authenticate(args['username'], args['password'])
        return {'token': app.tokens.token(user)}


@ns.route('/check')
class CheckToken(Resource):

    @ns.expect(token_request)
    @ns.marshal_with(token_response)
    @ns.doc(id='check_token')
    def post(self):
        """
        Check Token

        :raises Unauthorized: Check Token Failed
        """
        args = token_request.parse_args()
        user = app.tokens.load_user_from_token(args['token'])
        return {'token': args['token']}


@ns.route('/refresh')
class RefreshToken(Resource):
    @ns.expect(token_request)
    @ns.marshal_with(token_response)
    @ns.doc(id='refresh_token')
    def post(self):
        """
        Refresh Token

        :raises SecurityException: Refresh Token Failed
        """
        args = token_request.parse_args()
        user = app.rbac.tokens.load_user_from_token(args['token'])
        return {'token': app.tokens.token(user)}
