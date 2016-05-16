import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.bootstrap import Bootstrap
from flask.ext.pagedown import PageDown
from flask.ext.uploads import UploadSet, IMAGES, configure_uploads

db = SQLAlchemy()
lm = LoginManager()
bootstrap = Bootstrap()
pagedown = PageDown()
avatars = UploadSet('avatars', IMAGES)


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    db.init_app(app)
    lm.init_app(app)
    bootstrap.init_app(app)
    pagedown.init_app(app)
    configure_uploads(app, avatars)

    exists_db = os.path.isfile(app.config['DATABASE'])
    if not exists_db:
        import db_fill

    from app.main import main, auth, user, book, comment, log
    for blueprint in [main,auth, user, book, comment, log]:
        app.register_blueprint(blueprint)

    return app


from app import models
