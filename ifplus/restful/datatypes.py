# -*- coding: utf-8 -*-
from .patched import Model, fields

KEY_VALUE_PAIR = Model("KeyValuePair", {
    'key': fields.String(description='键'),
    'value': fields.String(description='值')
}, title="键值对")
