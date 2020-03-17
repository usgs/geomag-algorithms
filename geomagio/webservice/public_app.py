from __future__ import absolute_import, unicode_literals

import os
import flask

from . import data


def create_app():
    app = flask.Flask(__name__, instance_relative_config=True)
    # configure using environment variables
    app.config.update(os.environ)

    # connect modules
    data.init_app(app)

    # add default route
    @app.route("/")
    def index():
        return flask.render_template("index.html")

    return app
