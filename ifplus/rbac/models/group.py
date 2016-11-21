# -*- coding: utf-8 -*-
from .base import PropertiesEntity


class Group(LdapEntity):
    """User or Role Group"""
    D_FIELD = 'cn'
    ROOT = 'ou=Groups'
    OBJECT_CLASS = ['top', 'groupOfNames', 'configGroup']

    def __init__(self, dn=None, attrs=None):
        super(Group, self).__init__(dn=dn, attrs=attrs)
