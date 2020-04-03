"""Geomag Web Services

This is an Application Server Gateway Interface (ASGI) application
and can be run using uvicorn, or any other ASGI server:

    uvicorn geomagio.api:app

"""
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from . import ws


app = FastAPI()
app.mount("/ws", ws.app)


@app.get("/", include_in_schema=False)
async def redirect_to_ws():
    return RedirectResponse("/ws")
