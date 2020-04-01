from datetime import datetime
import enum
import os
from typing import Any, Dict, List, Union

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.responses import JSONResponse
from obspy import UTCDateTime, Stream
from starlette.responses import Response

from ...edge import EdgeFactory
from ...iaga2002 import IAGA2002Writer
from ...imfjson import IMFJSONWriter
from ...TimeseriesUtility import get_interval_from_delta
from .DataApiQuery import DataApiQuery, DataType, OutputFormat, SamplingPeriod


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


def format_error(
    status_code: int, exception: str, format: str, request: Request
) -> Response:
    """Assign error_body value based on error format."""
    if format == "json":

        error = JSONResponse(json_error(status_code, exception, request.url))

    else:
        error = Response(
            iaga2002_error(status_code, exception, request.url), media_type="text/plain"
        )

    return error


def format_timeseries(timeseries, query: DataApiQuery) -> Stream:
    """Formats timeseries into JSON or IAGA data

    Parameters
    ----------
    obspy.core.Stream
        timeseries object with requested data

    DataApiQuery
        parsed query object

    Returns
    -------
    unicode
        IAGA2002 or JSON formatted string.
    """
    if query.format == "json":
        return Response(
            IMFJSONWriter.format(timeseries, query.elements),
            media_type="application/json",
        )
    else:
        return Response(
            IAGA2002Writer.format(timeseries, query.elements), media_type="text/plain",
        )


def get_data_factory():
    """Reads environment variable to determine the factory to be used

    Returns
    -------
    data_factory
        Edge or miniseed factory object
    """
    data_type = os.getenv("DATA_TYPE", "edge")
    data_host = os.getenv("DATA_HOST", "cwbpub.cr.usgs.gov")
    data_port = os.getenv("DATA_PORT", 2060)

    if data_type == "edge":
        data_factory = EdgeFactory(host=data_host, port=data_port)
        return data_factory
    else:
        return None


def get_timeseries(query: DataApiQuery):
    """Get timeseries data

    Parameters
    ----------
     DataApiQuery
        parsed query object

    Returns
    -------
    obspy.core.Stream
        timeseries object with requested data
    """
    data_factory = get_data_factory()

    timeseries = data_factory.get_timeseries(
        starttime=UTCDateTime(query.starttime),
        endtime=UTCDateTime(query.endtime),
        observatory=query.id,
        channels=query.elements,
        type=query.data_type,
        interval=get_interval_from_delta(query.sampling_period),
    )
    return timeseries


def iaga2002_error(code: int, error: Exception, url: str) -> str:
    """Format iaga2002 error message.

    Returns
    -------
    error_body : str
        body of iaga2002 error message.
    """
    status_message = ERROR_CODE_MESSAGES[code]
    error_body = f"""Error {code}: {status_message}

{error}

Usage details are available from

Request:
{url}

Request Submitted:
{UTCDateTime().isoformat()}Z

Service Version:
{VERSION}
"""
    return error_body


def json_error(code: int, error: Exception, url: str) -> Dict:
    """Format json error message.

    Returns
    -------
    error_body : str
        body of json error message.
    """
    status_message = ERROR_CODE_MESSAGES[code]
    error_dict = {
        "type": "Error",
        "metadata": {
            "title": status_message,
            "status": code,
            "error": str(error),
            "generated": UTCDateTime().isoformat() + "Z",
            "url": str(url),
        },
    }
    return error_dict


def parse_query(
    id: str,
    starttime: datetime = Query(None),
    endtime: datetime = Query(None),
    elements: List[str] = Query(None),
    sampling_period: SamplingPeriod = Query(SamplingPeriod.HOUR),
    data_type: Union[DataType, str] = Query(DataType.VARIATION),
    format: OutputFormat = Query(OutputFormat.IAGA2002),
) -> DataApiQuery:

    if starttime == None:
        now = datetime.now()
        starttime = UTCDateTime(year=now.year, month=now.month, day=now.day)

    else:
        try:
            starttime = UTCDateTime(starttime)

        except Exception as e:
            raise ValueError(
                f"Bad starttime value '{starttime}'."
                " Valid values are ISO-8601 timestamps."
            )

    if endtime == None:
        endtime = starttime + (24 * 60 * 60 - 1)

    else:
        try:
            endtime = UTCDateTime(endtime)
        except Exception as e:
            raise ValueError(
                f"Bad endtime value '{endtime}'."
                " Valid values are ISO-8601 timestamps."
            ) from e
    params = DataApiQuery(
        id=id,
        starttime=starttime,
        endtime=endtime,
        elements=elements,
        sampling_period=sampling_period,
        data_type=data_type,
        format=format,
    )

    return params


app = FastAPI(docs_url="/data")


@app.exception_handler(ValueError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if "format" in request.query_params:
        data_format = str(request.query_params["format"])
    else:
        data_format = "iaga2002"
    return format_error(400, str(exc), data_format, request)


@app.get("/data/")
def get_data(request: Request, query: DataApiQuery = Depends(parse_query)):
    try:
        timeseries = get_timeseries(query)
        return format_timeseries(timeseries, query)
    except Exception as e:
        return format_error(500, e, query.format, request)
