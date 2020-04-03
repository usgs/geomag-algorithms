import datetime
from typing import Dict, Union

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from starlette.responses import RedirectResponse

from . import data, elements


ERROR_CODE_MESSAGES = {
    204: "No Data",
    400: "Bad Request",
    404: "Not Found",
    409: "Conflict",
    500: "Internal Server Error",
    501: "Not Implemented",
    503: "Service Unavailable",
}

VERSION = "version"


app = FastAPI(docs_url="/docs", openapi_prefix="/ws")
app.include_router(data.router)
app.include_router(elements.router)


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse("/ws/docs")


@app.exception_handler(ValueError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Value errors are user errors.
    """
    if "format" in request.query_params:
        data_format = str(request.query_params["format"])
    return format_error(400, str(exc), data_format, request)


@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Other exceptions are server errors.
    """
    if "format" in request.query_params:
        data_format = str(request.query_params["format"])
    return format_error(500, str(exc), data_format, request)


def format_error(
    status_code: int, exception: str, format: str, request: Request
) -> Response:
    """Assign error_body value based on error format."""
    if format == "json":
        return json_error(status_code, exception, request.url)
    else:
        return Response(
            text_error(status_code, exception, request.url), media_type="text/plain"
        )


def json_error(code: int, error: Exception, url: str) -> Dict:
    """Format json error message.

    Returns
    -------
    error_body : str
        body of json error message.
    """
    return {
        "type": "Error",
        "metadata": {
            "title": ERROR_CODE_MESSAGES[code],
            "status": code,
            "error": str(error),
            "generated": datetime.datetime.utcnow(),
            "url": str(url),
        },
    }


def text_error(code: int, error: Exception, url: str) -> str:
    """Format error message as plain text

    Returns
    -------
    error message formatted as plain text.
    """
    return f"""Error {code}: {ERROR_CODE_MESSAGES[code]}

{error}

Usage details are available from

Request:
{url}

Request Submitted:
{datetime.datetime.utcnow().isoformat()}

Service Version:
{VERSION}
"""
