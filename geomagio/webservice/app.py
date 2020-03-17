from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

from .public_app import create_app as create_public_app
from .restricted_app import create_app as create_restricted_app


def create_app():
    public_app = create_public_app()
    restricted_app = create_restricted_app()
    application = DispatcherMiddleware(public_app, {"/restricted": restricted_app})

    return application


application = create_app()

if __name__ == "__main__":
    run_simple(
        hostname="localhost",
        port=5000,
        application=application,
        use_reloader=True,
        use_debugger=True,
        use_evalex=True,
    )
