# -*- coding: utf-8 -*-
from .patched import Namespace, fields

ns = Namespace('datatypes',
               title='DataTypes',
               version='1.0',
               description='基本数据结构',
               tags='dt')

BOOLEAN_VALUE = ns.model('Boolean', {
    'boolean': fields.Boolean(title='布尔值', description='布尔值')
})

KEY_VALUE_PAIR = ns.model("KeyValuePair", {
    'key': fields.String(title='键', description='键值对的键'),
    'value': fields.String(title='值', description='键值对的值')
}, title="键值对")

KEY_VALUE_PAIRS = fields.List(fields.Nested(KEY_VALUE_PAIR))
