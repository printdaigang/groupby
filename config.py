import os
basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(basedir, 'app.db')

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE

SECRET_KEY = 'you-will-never-guess'
