from flask import url_for
from flask.ext.restful import Resource, marshal_with, fields
from app.models import Comment as model_Comment
from . import api, parser, default_count
from .fields import comment_fields, comment_detail_fields


@api.route('/comments/<int:comment_id>/')
class Comment(Resource):
    @marshal_with(comment_detail_fields)
    def get(self, comment_id):
        comment = model_Comment.query.get_or_404(comment_id)
        comment.uri = url_for('api.comment', comment_id=comment.id, _external=True)
        return comment


@api.route('/comments/')
class CommentList(Resource):
    @marshal_with({'comments': fields.List(fields.Nested(comment_fields)), 'next': fields.String, 'prev': fields.String,
                   'total': fields.Integer, 'pages_count': fields.Integer, 'current_page': fields.Integer})
    def get(self):
        args = parser.parse_args()
        page = args['page'] or 1
        count = args['count'] or default_count
        pagination = model_Comment.query.paginate(page=page, per_page=count)
        items = pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for('api.commentlist', page=page - 1, count=count, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('api.commentlist', page=page + 1, count=count, _external=True)
        return {'comments': items, 'prev': prev,
                'next': next,
                'total': pagination.total,
                'pages_count': pagination.pages,
                'current_page': pagination.page}
