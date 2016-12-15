# -*- coding: utf-8 -*-
from flask import jsonify, url_for
from flask_restplus import Api as OriginalApi
from werkzeug import exceptions as http_exceptions
from werkzeug.utils import cached_property

from .namespace import Namespace
from .swagger import Swagger


class Api(OriginalApi):

    @cached_property
    def __schema__(self):
        # The only purpose of this method is to pass custom Swagger class
        return Swagger(self).as_dict()

    def init_app(self, app):
        super(Api, self).init_app(app)
        app.errorhandler(http_exceptions.UnprocessableEntity.code)(handle_validation_error)

    def namespace(self, *args, **kwargs):
        # The only purpose of this method is to pass a custom Namespace class
        _namespace = Namespace(*args, **kwargs)
        self.add_namespace(_namespace)
        return _namespace

    @property
    def spec_url(self):
        return url_for(self.endpoint('specs'), _external=True, _scheme='https')

# Return validation errors as JSON
def handle_validation_error(err):
    exc = err.data['exc']
    return jsonify({
        'status': http_exceptions.UnprocessableEntity.code,
        'message': exc.messages
    }), http_exceptions.UnprocessableEntity.code