from flask import  url_for
from flask.ext.restful import Resource, marshal_with, fields
from app.models import User as model_User
from . import api, parser, default_count
from .fields import user_fields


@api.route('/users/<int:user_id>/')
class User(Resource):
    @marshal_with(user_fields)
    def get(self, user_id):
        user = model_User.query.get_or_404(user_id)
        user.uri = url_for('api.user', user_id=user_id, _external=True)
        return user


@api.route('/users/')
class UserList(Resource):
    @marshal_with({'users': fields.List(fields.Nested(user_fields)), 'next': fields.String, 'prev': fields.String,
                   'total': fields.Integer, 'pages_count': fields.Integer, 'current_page': fields.Integer,
                   'count': fields.Integer})
    def get(self):
        args = parser.parse_args()
        page = args['page'] or 1
        count = args['count'] or default_count
        pagination = model_User.query.paginate(page=page, per_page=count)
        items = pagination.items
        for item in items:
            item.uri = url_for('api.user', user_id=item.id, _external=True)
        prev = None
        if pagination.has_prev:
            prev = url_for('api.userlist', page=page - 1, count=count, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('api.userlist', page=page + 1, count=count, _external=True)
        return {'users': items, 'prev': prev,
                'next': next,
                'total': pagination.total,
                'pages_count': pagination.pages,
                'current_page': pagination.page,
                'count': count
                }
