# -*- coding: utf-8 -*-
from .base import BaseHelper
from ..models.role import Role


class RoleHelper(BaseHelper):
    """用户集合"""

    def __init__(self, ldap_connection, name=None):
        super(RoleHelper, self).__init__(ldap_connection, name=name)

    def entity_class(self):
        return Role

    def assign(self, role, user_dn):
        pass

    def deassign(self, role, user_dn):
        pass

    def get_all_descendants(self):
        pass