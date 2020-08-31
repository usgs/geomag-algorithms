import json
import os
import uuid

from fastapi import Depends, FastAPI, Request, Response

from ..db.session_table import delete_session, get_session, save_session
from .encryption import get_fernet
from .login import current_user, router as login_router, User
from .metadata import router as metadata_router
from .SessionMiddleware import SessionMiddleware


app = FastAPI(root_path="/ws/secure")

# NOTE: database used for sessions is started by ..app.app,
# which mounts this application at /ws/secure
app.add_middleware(
    middleware_class=SessionMiddleware,
    delete_session_callback=delete_session,
    get_session_callback=get_session,
    save_session_callback=save_session,
    encryption=get_fernet(
        os.getenv("SECRET_KEY", uuid.uuid4().hex),
        os.getenv("SECRET_SALT", "secret_salt"),
    ),
    path="/ws/secure",
    session_cookie="PHPSESSID",
)

# include login routes to manage user
app.include_router(login_router)
app.include_router(metadata_router)


@app.get("/")
async def index(request: Request, user: User = Depends(current_user)):
    """Route to demo user login."""
    if user:
        link = f"""
            Logged in as {user.email}<br/>
            <a href="{request.url_for("logout")}">Logout</a>
        """
    else:
        link = f'<a href="{request.url_for("login")}">Login</a>'
    return Response(
        f"""<!doctype html>
<html>
<body>
    {link}
    <pre>{json.dumps(request.session, indent=2)}</pre>
</body>
</html>""",
        media_type="text/html",
    )
