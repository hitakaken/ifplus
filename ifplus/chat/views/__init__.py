# -*- coding: utf-8 -*-
from flask import Blueprint
from ifplus.restful.patched import Namespace

namespace = Namespace('chats',
                      title='即时消息API',
                      version='1.0',
                      description='即时消息 RestFul API',
                      tags='chats')
chats_blueprint = Blueprint('chats', __name__)

from . import events
