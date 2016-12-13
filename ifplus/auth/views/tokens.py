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
authenticate_get_request = ns.parser()
authenticate_get_request.add_argument('username', required=True, location='args')
authenticate_get_request.add_argument('password', required=True, location='args')
authenticate_post_request = ns.parser()
authenticate_post_request.add_argument('username', required=True, location='form')
authenticate_post_request.add_argument('password', required=True, location='form')
# 令牌 请求
token_request = ns.parser()
token_request.add_argument('refresh_token', location='form')
# 令牌 响应
token_response = ns.model(name=u'Tokens', model={
    u'AuthToken': fields.String(title=u'令牌'),
    u'RefreshToken': fields.String(title=u'更新令牌')
})


@ns.route('/authenticate')
class Authenticate(Resource):
    @ns.expect(authenticate_get_request)
    # @ns.doc(id='authenticate')
    @ns.response(code=200, description=u'用户登录成功', model=token_response)
    def get(self):
        """
        Authenticate

        :raises NotFound:  User not found
        :raises Unauthorized:  Authenticate Failed
        """
        args = authenticate_get_request.parse_args()
        return app.tokens.authenticate(args['username'], args['password'], request)

    @ns.expect(authenticate_post_request)
    @ns.doc(id='authenticate')
    @ns.response(code=200, description=u'用户登录成功', model=token_response)
    def post(self):
        """
        Authenticate

        :raises NotFound:  User not found
        :raises Unauthorized:  Authenticate Failed
        """
        args = authenticate_post_request.parse_args()
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


