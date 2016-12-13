# -*- coding: utf-8 -*-
import copy
import datetime
import json
import random
import string
import time
from bson import ObjectId
from flask import jsonify
from hashids import Hashids
from jwcrypto import jwt, jwk
# print jwk.JWK(generate='oct', size=512).export()
from pymongo import IndexModel, ASCENDING, DESCENDING
from werkzeug.exceptions import NotFound
from ..models.token import TokenUser
from ifplus.data.helpers.mongo_utils import init_indexes
# import msgpack
# from flask import current_app as app
# from werkzeug.exceptions import NotFound
# from ifplus.rbac.helpers import constants
# from ifplus.rbac.models.user import User
#


# def get_callback_function(func, default_function=None, default_return=None):
#     if (func is None and default_function is None) or not callable(func):
#         func_return = func if func is not None else default_return
#
#         def return_func(input, **kwargs):
#             return func_return
#
#         return return_func
#     return func if func is not None else default_function
#
#
# class TokenHelper(object):
#     def __init__(self, jwt_config=None, token_config=None):
#         if jwt_config is None:
#             jwt_config = {}
#         if token_config is None:
#             token_config = {}
#         self.jwt_secret = get_callback_function(jwt_config.get('secret', constants.JWT_SECRET))
#         self.jwt_algorithm = get_callback_function(jwt_config.get('algorithm', constants.JWT_ALGORITHM))
#         self.jwt_expired = get_callback_function(jwt_config.get('expired', constants.JWT_EXPIRED_TIMEDELTA))
#         self.jwt_leeway = get_callback_function(jwt_config.get('leeway', constants.JWT_LEEWAY))
#         self.token_header = token_config.get('HEADER', 'AuthToken')
#
#     def encode(self, payload, **kwargs):
#         """生成JWT令牌"""
#         secret = self.jwt_secret(payload, **kwargs)
#         algorithm = self.jwt_algorithm(payload, **kwargs)
#         # iat = datetime.datetime.utcnow()
#         if 'exp' not in payload:
#             expired = datetime.datetime.utcnow() + self.jwt_expired(payload, **kwargs)
#             payload['exp'] = expired
#         jwt_token = jwt.encode(payload, secret, algorithm=algorithm, **kwargs)
#         return jwt_token
#
#     def decode(self, jwt_token, **kwargs):
#         """解码JWT令牌"""
#         secret = self.jwt_secret(jwt_token, **kwargs)
#         algorithm = self.jwt_algorithm(jwt_token, **kwargs)
#         try:
#             leeway = self.jwt_leeway(jwt_token, **kwargs)
#             return jwt.decode(jwt_token, secret, algorithms=[algorithm], leeway=leeway, **kwargs)
#         except jwt.ExpiredSignatureError:
#             # Signature has expired
#             raise jwt.ExpiredSignatureError
#         except jwt.DecodeError:
#             raise jwt.DecodeError
#
#     def encrypt(self, content, **kwargs):
#         return msgpack.packb(content, **kwargs)
#
#     def decrypt(self, encrypted, **kwargs):
#         return msgpack.unpackb(encrypted, **kwargs)
#
#     def load_user_from_request(self, request):
#         try:
#             if self.token_header in request.headers:
#                 return self.load_user_from_token(request.headers.get(self.token_header))
#             if self.token_header in request.cookies:
#                 return self.load_user_from_token(request.cookies.get(self.token_header))
#         except jwt.InvalidTokenError:
#             return None
#         return None
#
#     def load_user_from_token(self, token):
#         payload = self.decode(token)
#         info = payload.get('i')
#         return UserToken(
#             payload.get('n'),
#             info.get('i'),
#             alias=info.get('a', []),
#             roles=info.get('r', []),
#             groups=info.get('g', []))
#
#     def token_user(self, user):
#         roles = []
#         for role_name in user.roles:
#             role = app.rbac.roles.find_one(role_name)
#             roles.append(role.id)
#         return UserToken(user.name, user.id, alias=user.sn, roles=roles, groups=[])
#
#     def token(self, user):
#         if user is None:
#             raise NotFound('User not found.')
#         if isinstance(user, str):
#             return user
#         if isinstance(user, User):
#             user = self.token_user(user)
#         token = {
#             'n': user.account,
#             'i': {
#                 'i': user.id,
#                 'a': user.alias,
#                 'r': user.roles,
#                 'g': user.groups
#             }
#         }
#         print token
#         return self.encode(token)
#
#     def cookie(self, response, user=None):
#         if user is not None:
#             response.set_cookie(self.token_header, value=self.token(user))
#         else:
#             response.set_cookie(self.token_header, value='', expires=0)
#         return response

TOKEN_CACHE_PREFIX = 'Token:'
MONGO_INDEXES = [IndexModel([(u'sid', DESCENDING)], name=u'token_session_id')]

def timestamp():
    """获取当前时间戳，以秒为单位"""
    return int(time.mktime(datetime.datetime.now().timetuple()))


def random_string(length):
    """随机字符串"""
    return u''.join(
        [unicode((string.ascii_letters + string.digits)[x], 'utf-8') for x in random.sample(range(0, 62), length)]
    )


class Tokens(object):
    """令牌工具集"""
    def __init__(self, app):
        """初始化工具集，根据配置设置各种工具"""
        self.app = app
        config = app.config.get('TOKEN', {})
        expkey = config.get('JWK', {'generate': 'oct', 'size': 256})
        self.key = jwk.JWK(**expkey)
        self.jwt_sign_header = config.get('JWT_SIGN', {'alg': 'HS256'})
        self.jwt_encrypt_header = config.get('JWT_ENCRYPT', {'alg': 'A256KW', 'enc': 'A256CBC-HS512'})
        self.expired = config.get('EXPIRED', 3600)
        self.refresh_expired = config.get('REFRESH_EXPIRED', 36000)
        self.hashids = Hashids(salt=config.get('HASHIDS_SALT', 'hashids salt'))
        self.trusted_proxies = config.get('TRUST_PROXIES', set())
        self.supers = config.get('SUPERS', set())
        self.cookie_config = dict((k.lower(), v) for (k, v) in config.get('COOKIE', {}).items())

    def init_mongodb(self):
        init_indexes(self.app.mongo.db, u'tokens', MONGO_INDEXES)

    def generate_unique_token_id(self):
        """生成唯一令牌ID"""
        token_id = ObjectId()
        base = str(token_id)
        return self.hashids.encode(
            int(base[:8], base=16),
            int(base[8:16], base=16),
            int(base[16:], base=16)), token_id

    def get_remote_address(self, request):
        """获取用户访问IP"""
        route = request.access_route + [request.remote_addr]
        return next((addr for addr in reversed(route)
                            if addr not in self.trusted_proxies), request.remote_addr)

    @staticmethod
    def get_user_agent(request):
        """获取用户User-Agent"""
        return request.headers.get('User-Agent')

    def convert_ldap_user_to_records(self, user, roles, groups, request, now):
        """将LDAP用户转换为Python dict对象"""
        claims = {
            u'account': unicode(user.name),
            u'uid': user.id,
            u'display': unicode(user.displayName),
            u'alias': user.sn,
            u'roles': roles,
            u'groups': groups,
            u'exp': now + self.expired,
            u'iat': now,
            u'jti': self.generate_unique_token_id()[0]
        }
        saved = copy.deepcopy(claims)
        saved.update({
            u'user_agent': self.get_user_agent(request),
            u'remote_addr': self.get_remote_address(request),
        })
        return claims, saved

    def encrypt(self, claims):
        """加密JWT"""
        token = jwt.JWT(header=self.jwt_sign_header, claims=claims)
        token.make_signed_token(self.key)
        # etoken = jwt.JWT(header=self.jwt_encrypt_header, claims=token.serialize())
        # etoken.make_encrypted_token(self.key)
        # return etoken.serialize()
        return token.serialize()

    def decrypt(self, encrpyted):
        """解密JWT"""
        et = jwt.JWT(key=self.key, jwt=encrpyted)
        # st = jwt.JWT(key=self.key, jwt=et.claims)
        # return st.claims
        return et.claims

    def make_response(self, user, request):
        """将用户放入响应"""
        roles = []
        for role_name in user.roles:
            role = self.app.rbac.roles.find_one(role_name)
            roles.append(role.id)
        groups = []
        now = timestamp()
        session_id, token_id = self.generate_unique_token_id()
        claims, saved = self.convert_ldap_user_to_records(user, roles, groups, request, now)
        refresh_token = random_string(32)
        refresh_claims = {u'refresh': refresh_token, u'exp': now + self.refresh_expired}
        saved.update(refresh_claims)
        self.app.cache.set(
            TOKEN_CACHE_PREFIX + session_id,
            json.dumps(saved, encoding='utf-8', ensure_ascii=True),
            timeout=self.expired)
        saved.update({u'_id': token_id})
        saved.update({u'sid': session_id})
        self.app.mongo.db.tokens.insert(saved)
        resp = jsonify({
            u'AuthToken': self.encrypt(claims),
            u'RefreshToken': self.encrypt(refresh_claims)
        })
        salt = random_string(16)
        hashed = self.encrypt({'s': session_id + salt})[:-24]
        print self.cookie_config
        resp.set_cookie('SID', value=session_id + salt + hashed, **self.cookie_config)
        return resp

    def authenticate(self, username, password, request):
        """用户名密码认证"""
        user = self.app.rbac.users.authenticate(username, password)
        return self.make_response(user, request)

    def check_saved_user_and_request(self, saved, request):
        """通过User-Agent和访问IP来校验令牌是否被他人利用"""
        if saved[u'user_agent'] != self.get_user_agent(request):
            return False
        if saved[u'remote_addr'] != self.get_remote_address(request):
            return False
        return True

    def get_and_check_session_id(self, request):
        """将Cookie中Session_id取出并简单校验"""
        if 'SID' not in request.cookies:
            return None
        sid = request.cookies.get('SID')
        session_id = sid[:-40]
        salt = sid[-40:-24]
        if sid[-24:] == self.encrypt({'s': session_id + salt})[:-24]:
            return session_id
        else:
            return None

    def load_user_from_request(self, request):
        """根据请求获取用户"""
        try:
            session_id = self.get_and_check_session_id(request)
            if session_id is None:
                return None
            saved = json.loads(self.app.cache.get(TOKEN_CACHE_PREFIX + session_id), encoding='utf-8')
            if saved is None:
                return None
            if not self.check_saved_user_and_request(saved, request):
                return None
            return TokenUser(saved, self)
        except BaseException, error:
            print error
            return None

    def refresh_token(self, request, refresh_token):
        """刷新令牌"""
        refresh_claims = self.decrypt(refresh_token)
        now = timestamp()
        if now > refresh_claims[u'exp']:
            return None
        session_id = self.get_and_check_session_id(request)
        if session_id is None:
            return None
        saved = self.app.mongo.db.tokens.find_one({u'sid', session_id})
        if saved is None:
            return None
        user = self.app.rbac.users.find_by_iid(saved[u'uid'])
        if user is None:
            raise NotFound('User not found.')
        return self.make_response(user, request)


