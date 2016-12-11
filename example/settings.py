# -*- coding: utf-8 -*-
SERVER_IP = '10.1.80.180'

MONGO_HOST = SERVER_IP
MONGO_PORT = 27017
MONGO_DBNAME = 'ifplus'

REDIS_URL = 'redis://' + SERVER_IP + ':6379/0'

CACHE = {
    'CACHE_TYPE': 'redis',
    'CACHE_KEY_PREFIX': 'ifplus',
    'CACHE_REDIS_HOST': SERVER_IP,
    'CACHE_REDIS_PORT': '6379',
    'CACHE_REDIS_URL': 'redis://' + SERVER_IP + ':6379'
}

LDAP = {
    'BASE_DN': 'dc=chinaconsult,dc=com',
    'ROOT_DN': 'cn=Manager,dc=chinaconsult,dc=com',
    'ROOT_PW': 'secret',
    'URI': 'ldap://10.1.80.180',
    'OPTIONS': {
        'REQUIRE_CERT': True,
        # 'CACERTFILE': '/root/server.pem',
        'CACERTFILE': 'D:/Tools/ldap/OpenLDAP/secure/certs/server.pem',
        # 'CACERTFILE': 'D:/Tools/apacheds/server.pem',
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
