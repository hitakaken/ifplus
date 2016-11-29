# -*- coding: utf-8 -*-
from flask import Blueprint

chats_blueprint = Blueprint('chats', __name__)

from . import events
