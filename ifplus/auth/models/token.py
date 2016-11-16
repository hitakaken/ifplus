# -*- coding: utf-8 -*-
from flask_login import UserMixin


class UserSession(UserMixin):
    def __init__(self, uid, alias=None, roles=None, groups=None):
        self.id = uid
        self.alias = [] if alias is None else alias
        self.roles = [] if roles is None else roles
        self.groups = [] if groups is None else groups

    def sid(self):
        return u'u:' + self.id

    def sids(self):
        sids = [self.sid()]
        for uid in self.alias:
            sids.append(u'u:' + uid)
        for role in self.roles:
            sids.append(u'r:' + role)
        for group in self.groups:
            sids.append(u'g:' + group)
        return sids
