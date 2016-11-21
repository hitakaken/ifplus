# -*- coding: utf-8 -*-
MONGO_HOST = '10.1.80.180'
MONGO_PORT = 27017
MONGO_DBNAME = 'ifplus'

IFPLUS_DEVICES = {
    u'/': {
        'dtype': 0,
        'did': None,
        'root': u'/',
        'owner': u'root',
        'group': None,
        'mode': 0o040750,
        'acl': []
    },
    u'/home': {
        'dtype': 1,
        'root': '/',
        'owner': u'root',
        'group': None,
        'mode': 0o040750,
        'acl': []
    }
}
