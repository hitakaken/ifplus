# -*- coding: utf-8 -*-
from abc import ABCMeta
from ldap.cidict import cidict

from ..helpers.constants import *
from ..helpers.utils import *


class LdapEntity(object):
    """LDAP持久化对象抽象类"""
    IGNORE_ATTR_TYPES = []
    ID_FIELD = 'ou'
    ROOT = ''
    OB5ECT_CLASS = ['top', 'organizationalUnit']

    def __init__(self, dn=None, attrs=None, helper=None):
        self.__dict__['dn'] = dn
        if attrs is None:
            attrs = cidict()
        if isinstance(attrs, dict):
            attrs = cidict(attrs)
        self.__dict__['attrs'] = attrs
        self.__dict__['cached_attrs'] = None
        self.__dict__['helper'] = helper

    def __getattr__(self, attr_name):
        if attr_name in self.attrs:
            return self.attrs.get(attr_name)
        elif self.helper is not None:
            return self.helper.getattr(self, attr_name)
        else:
            raise AttributeError

    def __setattr__(self, key, value):
        if key in self.attrs:
            self.attrs[key] = value
        elif self.helper is not None:
            self.helper.setattr(self, key, value)
        else:
            raise AttributeError

    def cache(self):
        self.cached_attrs = self.attrs.copy()

    def iid(self):
        if FT_IID not in self.attrs:
            self.attrs[FT_IID] = [uuid()]
        return self.attrs[FT_IID][0]

    def fill(self):
        pass

    def update(self, attrs):
        for k, v in six.iteritems(attrs):
            setattr(self, k, v)
        return self


class PropertiesEntity(LdapEntity):
    """Fortress 含有属性的抽象类"""
    def __init__(self, dn=None, attrs=None, helper=None):
        super(PropertiesEntity, self).__init__(dn=dn, attrs=attrs, helper=helper)
        self.update_props()

    def generate_props(self):
        props = self.attrs.get('ftProps', [])
        if not isinstance(props, list):
            props = [props]
        return unflatten(map(lambda e: tuple(e.split(':', 1)), props))

    def update_props(self):
        self.__dict__['props'] = self.generate_props()

    def __getattr__(self, attr_name):
        if attr_name.lower() == 'properties' or attr_name.lower() == 'props':
            return self.__dict__.get('props', None)
        else:
            return LdapEntity.__getattr__(self, attr_name)

    def __setattr__(self, key, value):
        if key.lower() == 'properties' or key.lower() == 'props':
            self.attrs.update({'ftProps': map(
                lambda (k, v): '%s:%s' % (k, v),
                flatten(value) if value is not None else [])
            })
            self.update_props()
        else:
            LdapEntity.__setattr__(self, key, value)


class Config(PropertiesEntity):
    """Fortress 配置对象
    Fortress Configuration Realms"""
    ID_FIELD = 'cn'
    ROOT = 'ou=Config'
    OBJECT_CLASS = ['ftProperties', 'device']

    def __init__(self, dn=None, attrs=None, helper=None):
        super(Config, self).__init__(dn=dn, attrs=attrs, helper=helper)


class Constraint(object):
    __metaclass__ = ABCMeta

    def __init__(self, name=None,
                 timeout=None, begin_time=None, end_time=None, begin_date=None, end_date=None,
                 day_mask=None, begin_lock_date=None, end_lock_date=None,
                 **kwargs):
        self.name = name
        self.timeout = timeout
        self.begin_time = begin_time
        self.end_time = end_time
        self.begin_date = begin_date
        self.end_date = end_date
        self.day_mask = day_mask
        self.begin_lock_date = begin_lock_date
        self.end_lock_date = end_lock_date
        if 'raw_data' in kwargs:
            self.parse(kwargs.get('raw_data'))

    def raw_data(self):
        return '%s$%s$%s$%s$%s$%s$%s$%s$%s' % (
            self.name,
            xstr(self.timeout),
            xstr(self.begin_time),
            xstr(self.end_time),
            xstr(self.begin_date),
            xstr(self.end_date),
            xstr(self.begin_lock_date),
            xstr(self.end_lock_date),
            xstr(self.day_mask),
        )

    def parse(self, raw_data):
        chunks = raw_data.split('$')
        self.name = chunks[0]
        self.timeout = chunk(chunks, 1, mapping=convert_string_to_integer)
        self.begin_time = chunk(chunks, 2, mapping=convert_string_to_integer)
        self.end_time = chunk(chunks, 3, mapping=convert_string_to_integer)
        self.begin_date = chunk(chunks, 4, mapping=convert_string_to_integer)
        self.end_date = chunk(chunks, 5, mapping=convert_string_to_integer)
        self.begin_lock_date = chunk(chunks, 6, mapping=convert_string_to_integer)
        self.end_lock_date = chunk(chunks, 7, mapping=convert_string_to_integer)
        self.day_mask = chunk(chunks, 8, mapping=convert_string_to_integer)
