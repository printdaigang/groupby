from flask import url_for
from flask.ext.restful import Resource, marshal_with, fields
from app.models import Tag as model_Tag
from . import api, parser, default_count
from .fields import tag_fields, tag_detail_fields


@api.route('/books/tags/<int:tag_id>/')
class Tag(Resource):
    @marshal_with(tag_detail_fields)
    def get(self, tag_id):
        tag = model_Tag.query.get_or_404(tag_id)
        tag.uri = url_for('api.tag', tag_id=tag.id, _external=True)
        return tag


@api.route('/books/tags/')
class TagList(Resource):
    @marshal_with({'tags': fields.List(fields.Nested(tag_fields)), 'next': fields.String, 'prev': fields.String,
                   'total': fields.Integer, 'pages_count': fields.Integer, 'current_page': fields.Integer})
    def get(self):
        args = parser.parse_args()
        page = args['page'] or 1
        count = args['count'] or default_count * 2
        pagination = model_Tag.query.paginate(page=page, per_page=count)
        items = pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for('api.taglist', page=page - 1, count=count, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('api.taglist', page=page + 1, count=count, _external=True)
        return {'tags': items, 'prev': prev,
                'next': next,
                'total': pagination.total,
                'pages_count': pagination.pages,
                'current_page': pagination.page}
