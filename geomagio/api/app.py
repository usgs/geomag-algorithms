"""Geomag Web Services

This is an Application Server Gateway Interface (ASGI) application
and can be run using uvicorn, or any other ASGI server:

    uvicorn geomagio.api:app

"""
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from .db import database
from . import secure
from . import ws


app = FastAPI()
app.mount("/ws/secure", secure.app)
app.mount("/ws", ws.app)


@app.on_event("startup")
async def on_startup():
    await database.connect()


@app.on_event("shutdown")
async def on_shutdown():
    await database.disconnect()


@app.get("/", include_in_schema=False)
async def redirect_to_ws():
    return RedirectResponse("/ws")
