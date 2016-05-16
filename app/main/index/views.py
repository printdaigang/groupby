from flask import render_template, g
from flask.ext.login import current_user
from .forms import SearchForm
from app.models import User, Book, Comment, Log
from . import main
from app import db


@main.before_request
def before_request():
    g.user = current_user


@main.route('/')
def index():
    search_form = SearchForm()
    popular_books = Book.query.outerjoin(Log).group_by(Book.id).order_by(db.func.count(Log.id).desc()).limit(5)
    popular_users = User.query.outerjoin(Log).group_by(User.id).order_by(db.func.count(Log.id).desc()).limit(5)
    recently_comments = Comment.query.filter_by(deleted=0).order_by(Comment.edit_timestamp.desc()).limit(5)
    return render_template("index.html", books=popular_books, users=popular_users, recently_comments=recently_comments,
                           search_form=search_form)
