# -*- coding: utf-8 -*-
from .helpers.base import LdapConnection
from .helpers.configs import ConfigHelper
from .helpers.users import UserHelper
from .helpers.roles import RoleHelper
from .views.users import ns


class RBAC(object):
    def __init__(self, app=None, **kwargs):
        self.app = app
        self.connection = None
        self.configs = None
        self.users = None
        self.roles = None
        self.groups = None
        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        self.app = app
        # LDAP 定义
        self.connection = LdapConnection(ldap_config=app.config['LDAP'])
        self.connection.begin()
        # DAO 定义
        self.configs = ConfigHelper(self.connection, name='configs')
        self.users = UserHelper(self.connection, name='users')
        self.roles = RoleHelper(self.connection, name='roles')
        # 初始化
        self.connection.initialize()
        app.api.add_namespace(ns)
        setattr(app, 'rbac', self)
