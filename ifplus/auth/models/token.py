# -*- coding: utf-8 -*-
from flask_login import UserMixin

ADMIN_ROLE = u''


class TokenUser(UserMixin):
    def __init__(self, saved, tokens):
        self.account = saved[u'account']
        self.id = saved[u'uid']
        self.display = saved.get(u'display', self.account)
        self.alias = saved.get(u'alias',[])
        self.roles = saved.get(u'roles', [])
        self.groups = saved.get(u'groups', [])
        self.tokens = tokens

    @property
    def sid(self):
        return u'u:' + self.id

    @property
    def sids(self):
        sids = [self.sid]
        for uid in self.alias:
            sids.append(u'u:' + uid)
        for role in self.roles:
            sids.append(u'r:' + role)
        for group in self.groups:
            sids.append(u'g:' + group)
        return sids

    @property
    def is_admin(self):
        return ADMIN_ROLE in self.roles

    @classmethod
    def model(cls, ns):
        parser = ns.parser()
        parser.add_argument('AuthToken', location='headers')
        return parser

