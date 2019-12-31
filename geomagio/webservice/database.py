from __future__ import unicode_literals
from builtins import str

import flask
import flask_login
import flask_migrate
import flask_sqlalchemy


# database object
db = flask_sqlalchemy.SQLAlchemy()


def init_app(app: flask.Flask):
    db.init_app(app)
    migrate = flask_migrate.Migrate(app, db)


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.Text, unique=True, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    groups = db.Column(db.Text)

    def get_id(self) -> str:
        return str(self.openid)

    def to_dict(self):
        return {
            'id': self.id,
            'openid': self.openid,
            'email': self.email,
            'groups': self.groups
        }
