import os

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from obspy import UTCDateTime

from . import algorithms, data, elements, metadata, observatories


ERROR_CODE_MESSAGES = {
    204: "No Data",
    400: "Bad Request",
    404: "Not Found",
    409: "Conflict",
    500: "Internal Server Error",
    501: "Not Implemented",
    503: "Service Unavailable",
}

METADATA_ENDPOINT = bool(os.getenv("METADATA_ENDPOINT", False))
VERSION = os.getenv("GEOMAG_VERSION", "version")


app = FastAPI(docs_url="/docs", root_path="/ws")

app.include_router(algorithms.router)
app.include_router(data.router)
app.include_router(elements.router)
app.include_router(observatories.router)

if METADATA_ENDPOINT:
    app.include_router(metadata.router)


@app.middleware("http")
async def add_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers[
        "Access-Control-Allow-Headers"
    ] = "accept, origin, authorization, content-type"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Cache-Control"] = "max-age=60"
    return response


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
    # These urls are embedded in responses
    # and app usually runs behind reverse proxy
    url = str(request.url)
    usage = f"http://{request.headers['host']}/ws/docs"
    if "x-forwarded-proto" in request.headers:
        proto = f"{request.headers['x-forwarded-proto']}:"
        url = url.replace("http:", proto)
        usage = usage.replace("http:", proto)
    # serve error
    if format == "json":
        return json_error(code=status_code, error=exception, url=url, usage=usage)
    else:
        return text_error(code=status_code, error=exception, url=url, usage=usage)


def json_error(code: int, error: Exception, url: str, usage: str) -> Response:
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
                "url": url,
                "usage": usage,
                "version": VERSION,
            },
        },
        status_code=code,
    )


def text_error(code: int, error: Exception, url: str, usage: str = "") -> Response:
    """Format error message as plain text

    Returns
    -------
    error message formatted as plain text.
    """
    return PlainTextResponse(
        content=f"""Error {code}: {ERROR_CODE_MESSAGES[code]}

{error}

Usage details are available from {usage}

Request:
{url}

Request Submitted:
{UTCDateTime().isoformat()}Z

Service Version:
{VERSION}
""",
        status_code=code,
    )
