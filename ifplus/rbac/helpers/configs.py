# -*- coding: utf-8 -*-
from .base import BaseHelper
from ..models.base import Config


class ConfigHelper(BaseHelper):
    """配置集合"""
    def __init__(self, ldap_connection, name=None):
        super(ConfigHelper, self).__init__(ldap_connection, name=name)

    def entity_class(self):
        return Config
