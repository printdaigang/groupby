import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
bootstrap = Bootstrap(app)
exists_db = os.path.isfile(app.config['DATABASE'])
if not exists_db:
    import db_fill

from app import models, views
