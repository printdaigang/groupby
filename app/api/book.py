from flask import url_for
from flask.ext.restful import Resource, marshal_with, fields
from app.models import Book as model_Book
from . import api, parser, default_count
from .fields import book_fields, book_detail_fields


@api.route('/books/<int:book_id>/')
class Book(Resource):
    @marshal_with(book_detail_fields)
    def get(self, book_id):
        return model_Book.query.get_or_404(book_id)


@api.route('/books/')
class BookList(Resource):
    @marshal_with({'books': fields.List(fields.Nested(book_fields)), 'next': fields.String, 'prev': fields.String,
                   'total': fields.Integer, 'pages_count': fields.Integer, 'current_page': fields.Integer})
    def get(self):
        args = parser.parse_args()
        page = args['page'] or 1
        count = args['count'] or default_count
        pagination = model_Book.query.paginate(page=page, per_page=count)
        items = pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for('api.booklist', page=page - 1, count=count, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('api.booklist', page=page + 1, count=count, _external=True)
        return {'books': items, 'prev': prev,
                'next': next,
                'total': pagination.total,
                'pages_count': pagination.pages,
                'current_page': pagination.page}
