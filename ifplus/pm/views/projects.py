# -*- coding: utf-8 -*-
from ifplus.restful.patched import Namespace, Resource

ns = Namespace('pm',
               title='项目管理API',
               version='1.0',
               description='项目管理 RESTful API',
               tags='projects')


@ns.route('/<programme_name>/<project_name>')
class Projects(Resource):
    def post(self, programme_name, project_name):
        pass
