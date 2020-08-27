import os
from typing import Dict, Union

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from obspy import UTCDateTime

from . import algorithms, data, elements, observatories


ERROR_CODE_MESSAGES = {
    204: "No Data",
    400: "Bad Request",
    404: "Not Found",
    409: "Conflict",
    500: "Internal Server Error",
    501: "Not Implemented",
    503: "Service Unavailable",
}

VERSION = os.getenv("GEOMAG_VERSION", "version")


app = FastAPI(docs_url="/docs", root_path="/ws")

app.include_router(algorithms.router)
app.include_router(data.router)
app.include_router(elements.router)
app.include_router(observatories.router)


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse("/ws/docs")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Value errors are user errors."""
    data_format = (
        "format" in request.query_params
        and str(request.query_params["format"])
        or "text"
    )
    return format_error(400, str(exc), data_format, request)


@app.exception_handler(Exception)
async def server_exception_handler(request: Request, exc: Exception):
    """Other exceptions are server errors."""
    data_format = (
        "format" in request.query_params
        and str(request.query_params["format"])
        or "text"
    )
    return format_error(500, str(exc), data_format, request)


def format_error(
    status_code: int, exception: str, format: str, request: Request
) -> Response:
    """Assign error_body value based on error format."""
    if format == "json":
        return json_error(status_code, exception, request.url)
    else:
        return text_error(status_code, exception, request.url)


def json_error(code: int, error: Exception, url: str) -> Response:
    """Format json error message.

    Returns
    -------
    error_body : str
        body of json error message.
    """
    return JSONResponse(
        content={
            "type": "Error",
            "metadata": {
                "title": ERROR_CODE_MESSAGES[code],
                "status": code,
                "error": str(error),
                "generated": f"{UTCDateTime().isoformat()}Z",
                "url": str(url),
                "version": VERSION,
            },
        },
        status_code=code,
    )


def text_error(code: int, error: Exception, url: str) -> Response:
    """Format error message as plain text

    Returns
    -------
    error message formatted as plain text.
    """
    return PlainTextResponse(
        content=f"""Error {code}: {ERROR_CODE_MESSAGES[code]}

{error}

Usage details are available from

Request:
{url}

Request Submitted:
{UTCDateTime().isoformat()}Z

Service Version:
{VERSION}
""",
        status_code=code,
    )
