# -*- coding: utf-8 -*-
from ifplus.restful.patched import fields
from .base import PropertiesEntity
from ..helpers.utils import get_first


class User(PropertiesEntity):
    """Fortress People"""
    ID_FIELD = 'uid'
    ROOT = 'ou=People'
    OBJECT_CLASS = ['top', 'inetOrgPerson', 'organizationalPerson',
                    'ftUserAttrs', 'ftProperties', 'ftMods', 'extensibleObject']

    def __init__(self, dn=None, attrs=None, helper=None):
        super(User, self).__init__(dn=dn, attrs=attrs, helper=helper)

    def fill(self):
        if 'cn' not in self.attrs:
            self.attrs['cn'] = self.uid
        if 'sn' not in self.attrs:
            self.attrs['sn'] = self.uid
        if 'ou' not in self.attrs:
            self.attrs['ou'] = 'Public'

    @classmethod
    def model(cls, ns):
        return ns.model('UserInfo', {
            'dsp': fields.String(description='显示名', required=True),
            'id': fields.String(description='唯一标识')
        })

    def as_dict(self):
        return {
            'dsp': get_first(self.attrs['displayName']),
            'id': self.id
        }
