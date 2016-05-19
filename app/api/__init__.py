from flask import Blueprint
from flask.ext.restful import Api, reqparse
import types


def api_route(self, *args, **kwargs):
    def wrapper(cls):
        self.add_resource(cls, *args, **kwargs)
        return cls

    return wrapper


default_count = 5
parser = reqparse.RequestParser()
parser.add_argument('count', type=int, location='args')
parser.add_argument('page', type=int, location='args')

api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)

api.route = types.MethodType(api_route, api)

import user, book, comment, log, tag
