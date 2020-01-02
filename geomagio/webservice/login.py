from __future__ import absolute_import, unicode_literals, print_function
from builtins import str

import flask
import flask_login
import os
from authlib.integrations.flask_client import OAuth

from .database import db


# Blueprint for auth routes
blueprint = flask.Blueprint('login', __name__)
login_manager = flask_login.LoginManager()
oauth = OAuth()


def init_app(app: flask.Flask):
    """Flask app configuration method.
    """
    global blueprint
    global login_manager
    global oauth
    # LoginManager
    login_manager.init_app(app)
    login_manager.login_view = 'login.login'
    # OpenID client
    oauth.init_app(app)
    # register oauth client (needs to happen after init_app)
    # creates property "oauth.openid"
    oauth.register(
        name='openid',
        client_id=os.getenv('OPENID_CLIENT_ID'),
        client_secret=os.getenv('OPENID_CLIENT_SECRET'),
        server_metadata_url=os.getenv('OPENID_METADATA_URL'),
        client_kwargs={"scope": "openid email"}
    )
    # register blueprint routes
    app.register_blueprint(blueprint)


class User(db.Model, flask_login.UserMixin):
    """User database model.
    """
    __tablename__ = 'user'
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


@login_manager.user_loader
def _load_user(user_id: str):
    return User.query.filter_by(openid=user_id).first()


@blueprint.route('/hello')
@flask_login.login_required
def hello():
    return flask.render_template('hello.html')


@blueprint.route('/login')
def login():
    redirect_uri = flask.url_for('login.authorize', _external=True)
    return oauth.openid.authorize_redirect(redirect_uri)


@blueprint.route('/login/callback')
def authorize():
    oauth.openid.authorize_access_token()
    userinfo = oauth.openid.userinfo()
    # check if existing user
    user = User.query.filter_by(openid=userinfo.sub).first()
    if not user:
        user = User(openid=userinfo.sub, email=userinfo.email)
        db.session.add(user)
        db.session.commit()
    flask_login.login_user(user)
    return flask.redirect(flask.url_for('login.hello'))


@blueprint.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('index'))
