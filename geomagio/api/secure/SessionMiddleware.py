import base64
import json
from typing import Callable, Dict, Mapping
import uuid

from cryptography.fernet import Fernet
from starlette.datastructures import MutableHeaders, Secret
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class SessionMiddleware:
    """Based on Starlette SessionMiddleware.
    https://github.com/encode/starlette/blob/0.13.2/starlette/middleware/sessions.py

    Updated to store session id in cookie, and keep session data elsewhere.

    Usage:
        app.add_middleware(SessionMiddleware, **params)

    Parameters
    ----------
    app: the ASGI application

    delete_session_callback(session_id): callback to delete stored session data.
    get_session_callback(session_id): callback to get stored session data.
    save_session_callback(session_id): callback to update stored session data.
    encryption: encrypt session data before storage if provided

    session_cookie: name of session cookie
    path: path for session cookie
    max_age: how long session cookies last
    same_site: cookie same site policy
    https_only: whether to require https for cookies
    """

    def __init__(
        self,
        app: ASGIApp,
        delete_session_callback: Callable[[str], None],
        get_session_callback: Callable[[str], str],
        save_session_callback: Callable[[str, str], None],
        encryption: Fernet = None,
        session_cookie: str = "session",
        path: str = "/",
        max_age: int = 14 * 24 * 60 * 60,  # 14 days, in seconds
        same_site: str = "lax",
        https_only: bool = False,
    ) -> None:
        self.app = app
        self.encryption = encryption
        self.delete_session_callback = delete_session_callback
        self.get_session_callback = get_session_callback
        self.save_session_callback = save_session_callback
        self.session_cookie = session_cookie
        self.path = path
        self.max_age = max_age
        self.security_flags = "httponly; samesite=" + same_site
        if https_only:  # Secure flag can be used with HTTPS only
            self.security_flags += "; secure"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):  # pragma: no cover
            await self.app(scope, receive, send)
            return

        connection = HTTPConnection(scope)
        initial_session_was_empty = True
        session_id = None

        if self.session_cookie in connection.cookies:
            session_id = connection.cookies[self.session_cookie]
            try:
                scope["session"] = await self.get_session(session_id)
                initial_session_was_empty = False
            except Exception:
                scope["session"] = {}
        else:
            scope["session"] = {}

        async def send_wrapper(message: Message) -> None:
            nonlocal session_id
            if message["type"] == "http.response.start":
                if scope["session"]:
                    session_id = session_id or uuid.uuid4().hex
                    # Persist session
                    await self.save_session(session_id, scope["session"])
                    self.set_cookie(message=message, value=session_id)
                elif not initial_session_was_empty:
                    # Clear session
                    await self.delete_session(session_id)
                    self.set_cookie(message=message, value="null", max_age=-1)
            await send(message)

        await self.app(scope, receive, send_wrapper)

    async def delete_session(self, session_id: str):
        await self.delete_session_callback(session_id)

    async def get_session(self, session_id: str) -> Dict:
        data = await self.get_session_callback(session_id)
        if self.encryption:
            data = self.encryption.decrypt(data.encode("utf8"))
        return json.loads(data)

    async def save_session(self, session_id: str, data: Mapping):
        data = json.dumps(data)
        if self.encryption:
            data = self.encryption.encrypt(data.encode("utf8")).decode("utf8")
        await self.save_session_callback(session_id, data)

    def set_cookie(
        self,
        message: Message,
        value: str,
        max_age: int = None,
    ):
        headers = MutableHeaders(scope=message)
        headers.append("Cache-Control", "no-cache")
        headers.append(
            "Set-Cookie",
            f"{self.session_cookie}={value};"
            f" path={self.path};"
            f" Max-Age={max_age or self.max_age};"
            f" {self.security_flags}",
        )
