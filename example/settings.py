# -*- coding: utf-8 -*-
# SERVER_IP = '10.1.80.180'
# SERVER_IP = '106.14.20.122'
SERVER_IP = '127.0.0.1'

MONGO_HOST = SERVER_IP  # '106.14.20.122'
MONGO_PORT = 27017
MONGO_DBNAME = 'istis'

REDIS_URL = 'redis://' + SERVER_IP + ':6379/0'
REDIS_IP = SERVER_IP  # '192.168.25.105' # '10.1.80.180'

CACHE = {
    'CACHE_TYPE': 'redis',
    'CACHE_KEY_PREFIX': 'ifplus:',
    'CACHE_REDIS_HOST': REDIS_IP,
    'CACHE_REDIS_PORT': '6379',
    'CACHE_REDIS_URL': 'redis://' + REDIS_IP + ':6379',
    # 'CACHE_REDIS_PASSWORD': '123456'
}

LDAP = {
    'BASE_DN': 'dc=chinaconsult,dc=com',
    'ROOT_DN': 'cn=Manager,dc=chinaconsult,dc=com',
    'ROOT_PW': 'secret',
    'URI': 'ldap://' + SERVER_IP, # '106.14.20.122', #
    'OPTIONS': {
        # 'REQUIRE_CERT': True,
        # 'CACERTFILE': '/root/server.pem',
        # 'CACERTFILE': 'D:/Tools/ldap/OpenLDAP/secure/certs/server.pem',
        # 'CACERTFILE': 'D:/Tools/apacheds/server.pem',
        # 'DEBUG_LEVEL': 0
    },
    'START_TLS': False,
    'TRACE_LEVEL': 1
}

TOKEN = {
    'JWK': {"k":"KJexnbVD4LJoxpLJlq4lNFF2Jr8Cgm4E5iYiOJiWm5E","kty":"oct"},
    'JWT_SIGN': {'alg': 'HS256'},
    'JWT_ENCRYPT': {'alg': 'A256KW', 'enc': 'A256CBC-HS512'},
    'EXPIRED': 36000,
    'REFRESH_EXPIRED': 36000,
    'HASHIDS_SALT': 'hashids.chinaconsult.com',
    'TRUST_PROXIES': {'127.0.0.1'},
    'SUPERS': {'[Role]Administrators'},
    'COOKIE': {
        'DOMAIN': 'www.chinaconsult.com',
        # 'SECURE': True,
        'PATH': '/',
        # 'EXPIRES': 'Sat, 10 Dec 2016 23:38:25 GMT'
    }
}
JWT = {
    'secret': 'secret',
    'algorithm': 'HS256'
}

VFS = {
    'RID': '0000-0000-0000-0000',
    'ROOT': {
        u'uid':  u'[Role]Administrators',
        # u'uid': u'u:f3b4aeac-33ba-4924-8150-4bf697772b92',
        u'gid':  u'[RoleID]Administrators'
    },
    'DEVICES': {
        # '/home': {'type': 'nfs'},
        # '/www': {'type': 'local'},
        # '/projects': {'type': 'nfs'}
    }
}
