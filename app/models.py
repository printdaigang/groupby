# -*- coding: utf-8 -*-
from app import db
from flask.ext.login import UserMixin
from datetime import datetime, timedelta
import bleach
from markdown import markdown


class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    borrow_timestamp = db.Column(db.DateTime, default=datetime.now())
    return_timestamp = db.Column(db.DateTime, default=datetime.now())
    returned = db.Column(db.Boolean, default=0)

    def __init__(self, user, book):
        self.user = user
        self.book = book
        self.borrow_timestamp = datetime.now()
        self.return_timestamp = datetime.now() + timedelta(days=30)
        self.returned = 0

    def __repr__(self):
        return u'<%r - %r>' % (self.user.name, self.book.title)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(64))
    password = db.deferred(db.Column(db.String(128)))
    major = db.Column(db.String(128))
    admin = db.Column(db.Boolean, default=0)
    headline = db.Column(db.String(32), nullable=True)
    about_me = db.deferred(db.Column(db.Text, nullable=True))
    about_me_html = db.deferred(db.Column(db.Text, nullable=True))
    avatar = db.Column(db.String(128))

    logs = db.relationship('Log',
                           foreign_keys=[Log.user_id],
                           backref=db.backref('user', lazy='joined'),
                           lazy='dynamic',
                           cascade='all, delete-orphan')

    comments = db.relationship('Comment',
                               backref=db.backref('user', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')

    def __repr__(self):
        return u'<User name=%r email=%r>' % (self.name, self.email)

    def borrowing(self, book):
        return self.logs.filter_by(book_id=book.id, returned=0).first()

    def borrow_book(self, book):
        if self.logs.filter(Log.returned == 0, Log.return_timestamp < datetime.now()).count() > 0:
            return u"无法借阅,你有超期的图书未归还", 'danger'
        if self.borrowing(book):
            return u'貌似你已经借阅了这本书!!', 'warning'
        if not book.can_borrow():
            return u'这本书太火了,我们已经没有馆藏了,请等待别人归还以后再来借阅', 'danger'

        db.session.add(Log(self, book))
        return u'你成功GET到了一本 %s' % book.title, 'success'

    def return_book(self, log):
        if log.returned == 1 or log.user_id != self.id:
            return u'没有找到这条记录', 'danger'
        log.returned = 1
        log.return_timestamp = datetime.now()
        db.session.add(log)
        return u'你归还了一本 %s' % log.book.title, 'success'

    def avatar_url(self):
        from flask import url_for
        return self.avatar or url_for('static', filename='img/avatar.png')

    @staticmethod
    def on_changed_about_me(target, value, oldvalue, initiaor):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquate', 'code', 'em', 'i',
                        'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p']
        target.about_me_html = bleach.linkify(
            bleach.clean(markdown(value, output_format='html'),
                         tags=allowed_tags, strip=True))


db.event.listen(User.about_me, 'set', User.on_changed_about_me)


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(16), unique=True)
    title = db.Column(db.String(128))
    origin_title = db.Column(db.String(128))
    subtitle = db.Column(db.String(128))
    author = db.Column(db.String(128))
    translator = db.Column(db.String(64))
    publisher = db.Column(db.String(64))
    image = db.Column(db.String(128))
    pubdate = db.Column(db.String(32))
    tags = db.Column(db.String(128))
    pages = db.Column(db.Integer)
    price = db.Column(db.String(16))
    binding = db.Column(db.String(16))
    numbers = db.Column(db.Integer, default=5)
    summary = db.deferred(db.Column(db.Text, default=""))
    summary_html = db.deferred(db.Column(db.Text))
    catalog = db.deferred(db.Column(db.Text, default=""))
    catalog_html = db.deferred(db.Column(db.Text))
    hidden = db.Column(db.Boolean, default=0)

    logs = db.relationship('Log',
                           foreign_keys=[Log.book_id],
                           backref=db.backref('book', lazy='joined'),
                           lazy='dynamic',
                           cascade='all, delete-orphan')

    comments = db.relationship('Comment', backref='book',
                               lazy='dynamic',
                               cascade='all, delete-orphan')

    # def __init__(self, title, subtitle=None, author=None, isbn=None, category=None, description="", numbers=5):
    #     self.isbn = isbn
    #     self.title = title
    #     self.subtitle = subtitle
    #     self.author = author
    #     self.category = category
    #     self.description = description
    #     self.numbers = numbers

    def can_borrow(self):
        return Log.query.filter_by(book_id=self.id, returned=0).count() < self.numbers

    def can_borrow_number(self):
        return self.numbers - Log.query.filter_by(book_id=self.id, returned=0).count()

    @staticmethod
    def on_changed_summary(target, value, oldvalue, initiaor):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquate', 'code', 'em', 'i',
                        'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p']
        target.summary_html = bleach.linkify(
            bleach.clean(markdown(value, output_format='html'),
                         tags=allowed_tags, strip=True))

    @staticmethod
    def on_changed_catalog(target, value, oldvalue, initiaor):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquate', 'code', 'em', 'i',
                        'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p']
        target.catalog_html = bleach.linkify(
            bleach.clean(markdown(value, output_format='html'),
                         tags=allowed_tags, strip=True))

    def __repr__(self):
        return u'<Book %r>' % self.title


db.event.listen(Book.summary, 'set', Book.on_changed_summary)
db.event.listen(Book.catalog, 'set', Book.on_changed_catalog)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    comment = db.Column(db.String(1024))
    create_timestamp = db.Column(db.DateTime, default=datetime.now())
    edit_timestamp = db.Column(db.DateTime, default=datetime.now())
    deleted = db.Column(db.Boolean, default=0)

    def __init__(self, book, user, comment):
        self.user = user
        self.book = book
        self.comment = comment
        self.create_timestamp = datetime.now()
        self.edit_timestamp = self.create_timestamp
        self.deleted = 0
