# -*- coding:utf-8 -*-
from flask import abort
from flask.ext.login import current_user
from functools import wraps
from app import lm
from app.models import User


def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.admin:
            abort(403)
        return func(*args, **kwargs)

    return decorated_function


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


from .index import main
from .auth import auth
from .user import user
from .book import book
from .comment import comment
from .log import log
