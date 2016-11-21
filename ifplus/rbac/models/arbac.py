# -*- coding: utf-8 -*-
from ldap_rbac.core.models import LdapEntity, PropertiesEntity, Constraint


class ARBAC(LdapEntity):
    ID_FIELD = 'ou'
    ROOT = 'ou=ARBAC'


class UserOrgUnit(LdapEntity):
    """Fortress ARBAC User OrgUnit"""
    ID_FIELD = 'ou'
    ROOT = 'ou=OS-U,ou=ARBAC'
    OBJECT_CLASS = ['top', 'organizationalUnit', 'ftOrgUnit', 'ftMods']
    PARENT = ARBAC

    def __init__(self, dn=None, attrs=None, helper=None):
        super(UserOrgUnit, self).__init__(dn=dn, attrs=attrs, helper=helper)


class PermOrgUnit(LdapEntity):
    """Fortress ARBAC Perm OrgUnit"""
    ID_FIELD = 'ou'
    ROOT = 'ou=OS-P,ou=ARBAC'
    OBJECT_CLASS = ['top', 'organizationalUnit', 'ftOrgUnit', 'ftMods']
    PARENT = ARBAC

    def __init__(self, dn=None, attrs=None, helper=None):
        super(PermOrgUnit, self).__init__(dn=dn, attrs=attrs, helper=helper)


class AdminRole(PropertiesEntity):
    """Fortress Admin Role"""
    ID_FIELD = 'cn'
    ROOT = 'ou=AdminRole,ou=ARBAC'
    OBJECT_CLASS = ['top', 'organizationalRol', 'ftRls', 'ftProperties', 'ftPools', 'ftMods']
    PARENT = ARBAC

    def __init__(self, dn=None, attrs=None, helper=None):
        super(AdminRole, self).__init__(dn=dn, attrs=attrs, helper=helper)
