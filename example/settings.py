# -*- coding: utf-8 -*-
MONGO_HOST = '10.1.80.180'
MONGO_PORT = 27017
MONGO_DBNAME = 'ifplus'

LDAP = {
    'BASE_DN': 'dc=chinaconsult,dc=com',
    'ROOT_DN': 'cn=Manager,dc=chinaconsult,dc=com',
    'ROOT_PW': 'secret',
    'URI': 'ldap://10.1.80.180',
    'OPTIONS': {
        'REQUIRE_CERT': True,
        # 'CACERTFILE': '/root/server.pem',
        # 'CACERTFILE': 'D:/Tools/ldap/OpenLDAP/secure/certs/server.pem',
        'CACERTFILE': 'D:/Tools/apacheds/server.pem',
        # 'DEBUG_LEVEL': 0
    },
    'START_TLS': True,
    'TRACE_LEVEL': 1
}

TOKEN = {
    'HEADER': 'AuthToken',
    'SECRET': 'core',
    'EXPIRED': 36000
}
JWT = {
    'secret': 'secret',
    'algorithm': 'HS256'
}

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
