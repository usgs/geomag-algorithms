
import flask
import flask_migrate
import flask_sqlalchemy


# database object
db = flask_sqlalchemy.SQLAlchemy()


def init_app(app: flask.Flask):
    db.init_app(app)
    flask_migrate.Migrate(app, db)
