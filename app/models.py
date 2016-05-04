# -*- coding:utf-8 -*-
from app import db
from flask.ext.login import UserMixin
from datetime import datetime


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
        self.return_timestamp = datetime.now()
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

    about_me = db.deferred(db.Column(db.Text, nullable=True))

    logs = db.relationship('Log',
                           foreign_keys=[Log.user_id],
                           backref=db.backref('user', lazy='joined'),
                           lazy='dynamic',
                           cascade='all, delete-orphan')

    def __init__(self, email, name, password, major=None, admin=False, description=None):
        self.email = email
        self.name = name
        self.password = password
        self.major = major
        self.admin = admin
        self.description = description

    def __repr__(self):
        return u'<User name=%r email=%r>' % (self.name, self.email)

    def borrowing(self, book):
        return self.logs.filter_by(book_id=book.id, returned=0).first()

    def borrow_book(self, book):
        if self.borrowing(book):
            return u'貌似你已经借阅了这本书!!', 'warning'
        if not book.can_borrow():
            return u'这本书太火了,我们已经没有馆藏了,请等待别人归还以后再来借阅', 'danger'

        db.session.add(Log(self, book))
        return u'你成功GET到了一本 %s' % book.title, 'success'

    def return_book(self, lid):
        log = Log.query.get(lid)
        if log:
            if log.returned == 1 or log.user_id != self.id:
                return u'没有找到这条记录', 'danger'
            log.returned = 1
            log.return_timestamp = datetime.now()
            db.session.add(log)
            return u'你归还了一本 %s' % log.book.title, 'success'
        else:
            return u'没有找到这条记录', 'danger'

    def books_count(self):
        return self.logs.count()


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(32), unique=True)
    title = db.Column(db.String(128))
    subtitle = db.Column(db.String(256))
    author = db.Column(db.String(64))
    category = db.Column(db.String(64))
    description = db.deferred(db.Column(db.Text))
    numbers = db.Column(db.Integer, default=5)

    # logs = db.relationship('Log', backref='book', lazy='dynamic')

    logs = db.relationship('Log',
                           foreign_keys=[Log.book_id],
                           backref=db.backref('book', lazy='joined'),
                           lazy='dynamic',
                           cascade='all, delete-orphan')

    def __init__(self, title, subtitle=None, author=None, isbn=None, category=None, description=None, numbers=5):
        self.isbn = isbn
        self.title = title
        self.subtitle = subtitle
        self.author = author
        self.category = category
        self.description = description
        self.numbers = numbers

    def can_borrow(self):
        return Log.query.filter_by(book_id=self.id, returned=0).count() < self.numbers

    def can_borrow_number(self):
        return self.numbers - Log.query.filter_by(book_id=self.id, returned=0).count()

    def __repr__(self):
        return u'<Book %r>' % self.title
