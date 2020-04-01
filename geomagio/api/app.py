from fastapi import FastAPI

from .data.data_api import app as ws_app


app = FastAPI()


subapi = ws_app


app.mount("/ws", subapi)
