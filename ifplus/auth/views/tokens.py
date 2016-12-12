# -*- coding: utf-8 -*-
from flask import current_app as app, request
from werkzeug.exceptions import NotFound, Unauthorized
from ifplus.restful.patched import Namespace, Resource, fields


ns = Namespace('auth',
               title='认证授权 API',
               version='1.0',
               description='认证授权 RESTful API',
               tags='tokens')

# 验证 Form
authenticate_request = ns.parser()
authenticate_request.add_argument('username', required=True, location=['args','form'])
authenticate_request.add_argument('password', required=True, location=['args','form'])
# 令牌 请求
token_request = ns.parser()
token_request.add_argument('refresh_token', location='form')
# 令牌 响应
token_response = ns.model('Token', {
    'AuthToken': fields.String(title='令牌'),
    'RefreshToken': fields.String(title='更新令牌')
})


@ns.route('/authenticate')
class Authenticate(Resource):
    @ns.expect(authenticate_request)
    @ns.doc(id='authenticate',responses={'200': {'description': '用户认证成功', '$ref': '#/definitions/Token'}})
    def get(self):
        """
        Authenticate

        :raises NotFound:  User not found
        :raises Unauthorized:  Authenticate Failed
        """
        args = authenticate_request.parse_args()
        return app.tokens.authenticate(args['username'], args['password'], request)

    @ns.expect(authenticate_request)
    @ns.doc(id='authenticate',responses={'200': {'description': '用户认证成功', '$ref': '#/definitions/Token'}})
    def post(self):
        """
        Authenticate

        :raises NotFound:  User not found
        :raises Unauthorized:  Authenticate Failed
        """
        args = authenticate_request.parse_args()
        return app.tokens.authenticate(args['username'], args['password'], request)


@ns.route('/refresh')
class RefreshToken(Resource):
    @ns.expect(token_request)
    # @ns.marshal_with(token_response)
    @ns.doc(id='refresh_token')
    def post(self):
        """
        Refresh Token

        :raises Unauthorized: Refresh Token Failed
        """
        args = token_request.parse_args()
        return app.tokens.refresh_token(request, args['refresh_token'])


