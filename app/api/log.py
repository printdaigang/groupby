from flask import url_for
from flask.ext.restful import Resource, marshal_with, fields
from app.models import Log as model_Log
from . import api, parser, default_count
from .fields import logs_info_fields, logs_info_detail_fields


@api.route('/logs_info/<int:log_id>/')
class Log(Resource):
    @marshal_with(logs_info_detail_fields)
    def get(self, log_id):
        log = model_Log.query.get_or_404(log_id)
        log.uri = url_for('api.book', log_id=log.id, _external=True)
        return log


@api.route('/logs_info/')
class LogList(Resource):
    @marshal_with({'logs': fields.List(fields.Nested(logs_info_fields))})
    def get(self):
        args = parser.parse_args()
        page = args['page'] or 1
        count = args['count'] or default_count
        pagination = model_Log.query.paginate(page=page, per_page=count)
        items = pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for('api.loglist', page=page - 1, count=count, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('api.loglist', page=page + 1, count=count, _external=True)
        return {'logs': items, 'prev': prev,
                'next': next,
                'total': pagination.total,
                'pages_count': pagination.pages,
                'current_page': pagination.page,
                'count': count
                }
