# -*- coding: utf-8 -*-
import datetime
import jwt
import msgpack
from flask import current_app as app
from werkzeug.exceptions import NotFound
from ifplus.rbac.helpers import constants
from ifplus.rbac.models.user import User
from ..models.token import UserToken


def get_callback_function(func, default_function=None, default_return=None):
    if (func is None and default_function is None) or not callable(func):
        func_return = func if func is not None else default_return

        def return_func(input, **kwargs):
            return func_return

        return return_func
    return func if func is not None else default_function


class TokenHelper(object):
    def __init__(self, jwt_config=None, token_config=None):
        if jwt_config is None:
            jwt_config = {}
        if token_config is None:
            token_config = {}
        self.jwt_secret = get_callback_function(jwt_config.get('secret', constants.JWT_SECRET))
        self.jwt_algorithm = get_callback_function(jwt_config.get('algorithm', constants.JWT_ALGORITHM))
        self.jwt_expired = get_callback_function(jwt_config.get('expired', constants.JWT_EXPIRED_TIMEDELTA))
        self.jwt_leeway = get_callback_function(jwt_config.get('leeway', constants.JWT_LEEWAY))
        self.token_header = token_config.get('HEADER', 'AuthToken')

    def encode(self, payload, **kwargs):
        """生成JWT令牌"""
        secret = self.jwt_secret(payload, **kwargs)
        algorithm = self.jwt_algorithm(payload, **kwargs)
        # iat = datetime.datetime.utcnow()
        if 'exp' not in payload:
            expired = datetime.datetime.utcnow() + self.jwt_expired(payload, **kwargs)
            payload['exp'] = expired
        jwt_token = jwt.encode(payload, secret, algorithm=algorithm, **kwargs)
        return jwt_token

    def decode(self, jwt_token, **kwargs):
        """解码JWT令牌"""
        secret = self.jwt_secret(jwt_token, **kwargs)
        algorithm = self.jwt_algorithm(jwt_token, **kwargs)
        try:
            leeway = self.jwt_leeway(jwt_token, **kwargs)
            return jwt.decode(jwt_token, secret, algorithms=[algorithm], leeway=leeway, **kwargs)
        except jwt.ExpiredSignatureError:
            # Signature has expired
            raise jwt.ExpiredSignatureError
        except jwt.DecodeError:
            raise jwt.DecodeError

    def encrypt(self, content, **kwargs):
        return msgpack.packb(content, **kwargs)

    def decrypt(self, encrypted, **kwargs):
        return msgpack.unpackb(encrypted, **kwargs)

    def load_user_from_request(self, request):
        try:
            if self.token_header in request.headers:
                return self.load_user_from_token(request.headers.get(self.token_header))
            if self.token_header in request.cookies:
                return self.load_user_from_token(request.cookies.get(self.token_header))
        except jwt.InvalidTokenError:
            return None
        return None

    def load_user_from_token(self, token):
        payload = self.decode(token)
        info = payload.get('i')
        return UserToken(
            payload.get('n'),
            info.get('i'),
            alias=info.get('a', []),
            roles=info.get('r', []),
            groups=info.get('g', []))

    def token_user(self, user):
        roles = []
        for role_name in user.roles:
            role = app.rbac.roles.find_one(role_name)
            roles.append(role.id)
        return UserToken(user.name, user.id, alias=user.sn, roles=roles, groups=[])

    def token(self, user):
        if user is None:
            raise NotFound('User not found.')
        if isinstance(user, str):
            return user
        if isinstance(user, User):
            user = self.token_user(user)
        token = {
            'n': user.account,
            'i': {
                'i': user.id,
                'a': user.alias,
                'r': user.roles,
                'g': user.groups
            }
        }
        print token
        return self.encode(token)

    def cookie(self, response, user=None):
        if user is not None:
            response.set_cookie(self.token_header, value=self.token(user))
        else:
            response.set_cookie(self.token_header, value='', expires=0)
        return response
