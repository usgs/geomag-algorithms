from datetime import datetime
from fastapi import FastAPI, Query, Request
from json import dumps
from obspy import UTCDateTime
import os
from pydantic import BaseModel
from starlette.responses import Response
from typing import List, Any


from ..edge import EdgeFactory
from ..iaga2002 import IAGA2002Writer
from ..imfjson import IMFJSONWriter
from ..TimeseriesUtility import get_interval_from_delta


DEFAULT_DATA_TYPE = "variation"
DEFAULT_ELEMENTS = ["X", "Y", "Z", "F"]
DEFAULT_OUTPUT_FORMAT = "iaga2002"
DEFAULT_SAMPLING_PERIOD = "60"
DEFAULT_STARTTIME = datetime.now()
ERROR_CODE_MESSAGES = {
    204: "No Data",
    400: "Bad Request",
    404: "Not Found",
    409: "Conflict",
    500: "Internal Server Error",
    501: "Not Implemented",
    503: "Service Unavailable",
}
REQUEST_LIMIT = 345600
VALID_DATA_TYPES = ["variation", "adjusted", "quasi-definitive", "definitive"]
VALID_ELEMENTS = [
    "D",
    "DIST",
    "DST",
    "E",
    "E-E",
    "E-N",
    "F",
    "G",
    "H",
    "SQ",
    "SV",
    "UK1",
    "UK2",
    "UK3",
    "UK4",
    "X",
    "Y",
    "Z",
]
VALID_OBSERVATORIES = [
    "BDT",
    "BOU",
    "BRT",
    "BRW",
    "BSL",
    "CMO",
    "CMT",
    "DED",
    "DHT",
    "FDT",
    "FRD",
    "FRN",
    "GUA",
    "HON",
    "NEW",
    "SHU",
    "SIT",
    "SJG",
    "SJT",
    "TST",
    "TUC",
    "USGS",
]
VALID_OUTPUT_FORMATS = ["iaga2002", "json"]
VALID_SAMPLING_PERIODS = [0.1, 1, 60, 3600, 86400]
VERSION = "version"


app = FastAPI(docs_url="/data")


class WebServiceException(Exception):
    """Base class for exceptions thrown by web services."""

    pass


class WebServiceQuery(BaseModel):
    observatory_id: str
    starttime: Any
    endtime: Any
    elements: List[str] = DEFAULT_ELEMENTS
    sampling_period: int = DEFAULT_SAMPLING_PERIOD
    data_type: str = DEFAULT_DATA_TYPE
    output_format: str = DEFAULT_OUTPUT_FORMAT


@app.get("/data/")
def read_query(
    request: Request,
    id: str,
    starttime: Any = Query(DEFAULT_STARTTIME),
    endtime: Any = Query(None),
    elements: List[str] = Query(DEFAULT_ELEMENTS),
    sampling_period: float = Query(DEFAULT_SAMPLING_PERIOD),
    data_type: str = Query(DEFAULT_DATA_TYPE),
    format: str = Query(DEFAULT_OUTPUT_FORMAT),
):
    if len(elements) == 1 and "," in elements[0]:
        elements = [e.strip() for e in elements[0].split(",")]

    observatory = {
        "observatory_id": id,
        "starttime": starttime,
        "endtime": endtime,
        "elements": elements,
        "sampling_period": sampling_period,
        "data_type": data_type,
        "output_format": format,
    }

    try:
        parsed_query = parse_query(observatory)
        validate_query(parsed_query)
    except Exception as e:
        return format_error(400, e, format, request)

    try:
        timeseries = get_timeseries(parsed_query)
        return format_timeseries(timeseries, parsed_query)
    except Exception as e:
        return format_error(500, e, format, request)


def format_error(status_code, exception, format, request):
    if format == "json":
        error = Response(
            json_error(status_code, exception, request), media_type="application/json"
        )
    else:
        error = Response(
            iaga2002_error(status_code, exception, request), media_type="text/plain"
        )

    return error


def format_timeseries(timeseries, query):
    """Formats timeseries into JSON or IAGA data

    Parameters
    ----------
    obspy.core.Stream
        timeseries object with requested data

    WebServiceQuery
        parsed query object

    Returns
    -------
    unicode
        IAGA2002 or JSON formatted string.
    """
    if query.output_format == "json":
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


def get_timeseries(query):
    """Get timeseries data

    Parameters
    ----------
     WebServiceQuery
        parsed query object

    Returns
    -------
    obspy.core.Stream
        timeseries object with requested data
    """
    data_factory = get_data_factory()

    timeseries = data_factory.get_timeseries(
        query.starttime,
        query.endtime,
        query.observatory_id,
        query.elements,
        query.data_type,
        get_interval_from_delta(query.sampling_period),
    )
    return timeseries


def iaga2002_error(status_code, error, request):
    status_message = ERROR_CODE_MESSAGES[status_code]
    error_body = f"""Error {status_code}: {status_message}

{error}

Usage details are available from

Request:
{request.url}

Request Submitted:
{UTCDateTime().isoformat()}Z

Service Version:
{VERSION}
"""
    return error_body


def json_error(code: int, error: Exception, request):
    """Format json error message.

    Returns
    -------
    error_body : str
        body of json error message.
    """
    status_message = ERROR_CODE_MESSAGES[code]
    url = request.url.__dict__
    error_dict = {
        "type": "Error",
        "metadata": {
            "title": status_message,
            "status": code,
            "error": str(error),
            "generated": UTCDateTime().isoformat() + "Z",
            "url": url,
        },
    }
    return dumps(error_dict).encode("utf8")


def parse_query(query):

    try:
        query["starttime"] = UTCDateTime(query["starttime"])

    except Exception as e:
        raise WebServiceException(
            f"Bad starttime value '{query['starttime']}'."
            " Valid values are ISO-8601 timestamps."
        ) from e

    if query["endtime"] == None:
        endtime = query["starttime"] + (24 * 60 * 60 - 1)
        query["endtime"] = endtime

    else:
        try:
            endtime = query["endtime"]
            endtime = UTCDateTime(endtime)
            query["endtime"] = endtime
        except Exception as e:
            raise WebServiceException(
                f"Bad endtime value '{query['endtime']}'."
                " Valid values are ISO-8601 timestamps."
            ) from e

    params = WebServiceQuery(**query)
    return params


def validate_query(query):
    if query.data_type not in VALID_DATA_TYPES:
        raise WebServiceException(
            f"Bad data type value '{query.data_type}'."
            f" Valid values are: {', '.join(VALID_DATA_TYPES)}."
        )
    if query.observatory_id not in VALID_OBSERVATORIES:
        raise WebServiceException(
            f"Bad observatory id '{query.observatory_id}'."
            f" Valid values are: {', '.join(VALID_OBSERVATORIES)}."
        )
    if query.output_format not in VALID_OUTPUT_FORMATS:
        raise WebServiceException(
            f"Bad format value '{query.output_format}'."
            f" Valid values are: {', '.join(VALID_OUTPUT_FORMATS)}."
        )
    if query.sampling_period not in VALID_SAMPLING_PERIODS:
        raise WebServiceException(
            f"Bad sampling_period value '{query.sampling_period}'."
            f" Valid values are: {', '.join(VALID_SAMPLING_PERIODS)}."
        )
    # validate combinations
    if len(query.elements) > 4 and query.output_format == "iaga2002":
        raise WebServiceException(
            "No more than four elements allowed for iaga2002 format."
        )
    if query.starttime > query.endtime:
        raise WebServiceException("starttime must be before endtime.")
    # check data volume
    samples = int(
        len(query.elements) * (query.endtime - query.starttime) / query.sampling_period
    )
    if samples > REQUEST_LIMIT:
        raise WebServiceException(f"Query exceeds request limit ({samples} > 345600)")
