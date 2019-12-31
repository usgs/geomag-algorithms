from __future__ import absolute_import

import flask
import flask_session

from .database import db


def init_app(app: flask.Flask):
    app.config['SESSION_TYPE'] = 'sqlalchemy'
    app.config['SESSION_SQLALCHEMY'] = db
    flask_session.Session(app)
