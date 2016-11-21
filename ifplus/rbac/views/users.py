# -*- coding: utf-8 -*-
from flask import current_app as app
from werkzeug.exceptions import NotFound

from ifplus.restful.patched import Namespace, Resource
from ..models.user import User
from ..models.role import Role

ns = Namespace('usr',
               title='用户系统API',
               version='1.0',
               description='用户系统 RESTful API',
               tags='users')

# 用户管理对象 Schema
user_model = User.model(ns)
role_model = Role.model(ns)


@ns.route('/info/<uid>')
class UserInfo(Resource):
    @ns.doc(id='user_info')
    @ns.marshal_with(user_model)
    def get(self, uid):
        user = app.rbac.users.find_by_iid(uid)
        if user is None:
            raise NotFound('User not found.')
        return user.as_dict()


@ns.route('/role/<rid>')
class RoleInfo(Resource):
    @ns.doc(id='role_info')
    @ns.marshal_with(role_model)
    def get(self, rid):
        role = app.rbac.roles.find_by_iid(rid)
        if role is None:
            raise NotFound('Role not found.')
        return role.as_dict()
