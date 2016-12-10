# -*- coding: utf-8 -*-
from flask_login import UserMixin

ADMIN_ROLE = u''


class UserToken(UserMixin):
    def __init__(self, account, uid, alias=None, roles=None, groups=None):
        self.account = account
        self.id = uid
        self.alias = [] if alias is None else alias
        self.roles = [] if roles is None else roles
        self.groups = [] if groups is None else groups

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

