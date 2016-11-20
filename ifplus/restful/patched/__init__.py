# -*- coding: utf-8 -*-
# See https://github.com/frol/flask-restplus-server-example

from flask_restplus import *
from .api import Api
from .model import Schema, DefaultHTTPErrorSchema
from .namespace import Namespace
from .parameters import Parameters, PostFormParameters, PatchJSONParameters
from .swagger import Swagger
from .resource import Resource
import flask_marshmallow
if flask_marshmallow.has_sqla:
    from .model import ModelSchema
