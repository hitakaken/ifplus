# -*- coding: utf-8 -*-
from flask import current_app as app
from werkzeug.exceptions import NotFound, BadRequest

from ifplus.restful.patched import Namespace, Resource
from ..models.user import User
from ..models.role import Role

# authenticate
# isUserMemberOf
# find
# findUser
# findGroup
# findUsers
# findGroups
# groupExists
# userExists
# getGroupMembershipForGroup
# getGroupMembershipForUser
# getUsersForGroup
# getRootDSE
# findDeletedObjects

ns = Namespace('usr',
               title='用户系统API',
               version='1.0',
               description='用户系统 RESTful API',
               tags='users')

# 用户管理对象 Schema
user_model = User.model(ns)
role_model = Role.model(ns)
search_request_model = ns.parser()
search_request_model.add_argument('q', location='args', required=True)


@ns.route('/info/<uid>')
class UserInfo(Resource):
    @ns.doc(id='user_info')
    @ns.marshal_with(user_model)
    def get(self, uid):
        user = app.rbac.users.find_by_iid(uid)
        if user is None:
            raise NotFound('User not found.')
        return user.as_dict()


@ns.route('/search')
class UserSearch(Resource):
    @ns.expect(search_request_model)
    @ns.doc(id='search_users')
    @ns.marshal_list_with(user_model)
    def post(self):
        args = search_request_model.parse_args()
        if args['q'] is None or len(args['q']) < 1:
            raise BadRequest('Query is wrong')
        users = app.rbac.users.find_all({'sn': args['q'] + '*'})
        return [user.as_dict() for user in users]


@ns.route('/role/<rid>')
class RoleInfo(Resource):
    @ns.doc(id='role_info')
    @ns.marshal_with(role_model)
    def get(self, rid):
        role = app.rbac.roles.find_by_iid(rid)
        if role is None:
            raise NotFound('Role not found.')
        return role.as_dict()


@ns.route('/role/search')
class RoleSearch(Resource):
    @ns.expect(search_request_model)
    @ns.doc(id='search_roles')
    @ns.marshal_list_with(role_model)
    def post(self):
        args = search_request_model.parse_args()
        if args['q'] is None or len(args['q']) < 1:
            raise BadRequest('Query is wrong')
        roles = app.rbac.roles.find_all({'cn': args['q'] + '*'})
        return [role.as_dict() for role in roles]