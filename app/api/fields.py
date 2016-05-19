from app.models import Log as model_Log, Comment as model_Comment
from flask.ext.restful import fields
from flask import url_for
from . import default_count

user_fields = {
    'id': fields.Integer,
    'email': fields.String,
    'name': fields.String,
    'major': fields.String,
    'headline': fields.String,
    'about_me': fields.String,
    'about_me_html': fields.String,
    'avatar': fields.String(attribute=lambda x: x.avatar_url(_external=True)),
    'uri': fields.String(attribute=lambda x: url_for('api.user', tag_id=x.id, _external=True)),
}

tag_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'books_count': fields.Integer(attribute=lambda x: x.books.count()),
    'uri': fields.String(attribute=lambda x: url_for('api.tag', tag_id=x.id, _external=True)),
}

book_fields = {
    'id': fields.Integer,
    'isbn': fields.String,
    'title': fields.String,
    'origin_title': fields.String,
    'subtitle': fields.String,
    'author': fields.String,
    'translator': fields.String,
    'publisher': fields.String,
    'image': fields.String,
    'pubdate': fields.String,
    'pages': fields.Integer,
    'price': fields.String,
    'binding': fields.String,
    'numbers': fields.Integer,
    'hidden': fields.Boolean,
    'can_borrow': fields.Boolean(attribute=lambda x: x.can_borrow()),
    'can_borrow_number': fields.Integer(attribute=lambda x: x.can_borrow_number()),
    'tags': fields.List(fields.Nested(tag_fields), attribute=lambda x: x.tags),
    'uri': fields.String(attribute=lambda x: url_for('api.book', book_id=x.id, _external=True)),
}

logs_info_fields = {
    'id': fields.Integer,
    'user_id': fields.Integer,
    'user_name': fields.String(attribute=lambda x: x.user.name),
    'book_id': fields.Integer,
    'book_title': fields.String(attribute=lambda x: x.book.title),
    'borrow_timestamp': fields.DateTime(dt_format='rfc822'),
    'return_timestamp': fields.DateTime(dt_format='rfc822'),
    'returned': fields.Boolean,
    'uri': fields.String(attribute=lambda x: url_for('api.log', log_id=x.id, _external=True)),
}

comment_fields = {
    'id': fields.Integer,
    'user_id': fields.Integer,
    'user_name': fields.String(attribute=lambda x: x.user.name),
    'book_id': fields.Integer,
    'book_title': fields.String(attribute=lambda x: x.book.title),
    'comment': fields.String,
    'create_timestamp': fields.DateTime,
    'edit_timestamp': fields.DateTime,
    'deleted': fields.Boolean,
    'uri': fields.String(attribute=lambda x: url_for('api.comment', comment_id=x.id, _external=True)),
}

comment_detail_fields = dict(comment_fields, **{
    'user': fields.Nested(user_fields, attribute=lambda x: x.user),
    'book': fields.Nested(book_fields, attribute=lambda x: x.book),
})

book_detail_fields = \
    dict(book_fields,
         **{'summary': fields.String,
            'summary_html': fields.String,
            'catalog': fields.String,
            'catalog_html': fields.String,
            'borrowing_logs': fields.List(fields.Nested(logs_info_fields),
                                          attribute=lambda x: x.logs.filter_by(returned=0).order_by(
                                              model_Log.id.desc()).limit(default_count)),
            'borrowing_logs_id': fields.List(fields.Integer, attribute=lambda x: [e.id for e in
                                                                                  x.logs.filter_by(returned=0).order_by(
                                                                                      model_Log.id.desc()).all()]),
            'borrowied_logs': fields.List(fields.Nested(logs_info_fields),
                                          attribute=lambda x: x.logs.filter_by(returned=1).order_by(
                                              model_Log.id.desc()).limit(default_count)),
            'borrowed_logs_id': fields.List(fields.Integer, attribute=lambda x: [e.id for e in
                                                                                 x.logs.filter_by(returned=1).order_by(
                                                                                     model_Log.id.desc()).all()]),
            'comments': fields.List(fields.Nested(comment_fields),
                                    attribute=lambda x: x.comments.filter_by(deleted=0).order_by(
                                        model_Comment.id.desc()).limit(default_count)),
            'comments_id': fields.List(fields.Integer, attribute=lambda x: [e.id for e in
                                                                            x.comments.filter_by(deleted=0).order_by(
                                                                                model_Comment.id.desc()).all()])
            }
         )

logs_info_detail_fields = dict(logs_info_fields, **{'user': fields.Nested(user_fields, attribute=lambda x: x.user),
                                                    'book': fields.Nested(book_fields, attribute=lambda x: x.book)})

tag_detail_fields = dict(tag_fields, **{'books': fields.List(fields.Nested(book_fields), attribute=lambda x: x.books)})
