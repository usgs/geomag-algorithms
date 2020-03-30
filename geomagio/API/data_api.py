from datetime import datetime
import enum
from json import dumps
import os
from typing import List, Any, Union

from fastapi import FastAPI, Query, Request, Depends, HTTPException
from obspy import UTCDateTime
from pydantic import BaseModel, validator, ValidationError, root_validator
from starlette.responses import PlainTextResponse, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ..edge import EdgeFactory
from ..iaga2002 import IAGA2002Writer
from ..imfjson import IMFJSONWriter
from ..TimeseriesUtility import get_interval_from_delta
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)


DEFAULT_DATA_TYPE = "variation"
DEFAULT_ELEMENTS = ["X", "Y", "Z", "F"]
DEFAULT_OUTPUT_FORMAT = "iaga2002"
DEFAULT_SAMPLING_PERIOD = 60
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
VERSION = "version"

app = FastAPI(docs_url="/data")


class DataType(str, enum.Enum):
    VARIATION = "variation"
    ADJUSTED = "adjusted"
    QUASI_DEFINITIVE = "quasi-definitive"
    DEFINITIVE = "definitive"


class OutputFormat(str, enum.Enum):
    IAGA2002 = "iaga2002"
    JSON = "json"


class SamplingPeriod(float, enum.Enum):
    TEN_HERTZ = 0.1
    SECOND = 1.0
    MINUTE = 60
    HOUR = 3600
    DAY = 86400


class WebServiceQuery(BaseModel):
    id: str
    starttime: Any
    endtime: Any
    elements: List[str]
    sampling_period: SamplingPeriod
    data_type: Union[DataType, str]
    format: OutputFormat

    @validator("data_type")
    def validate_data_type(cls, data_type):
        if len(data_type) != 2 and data_type not in DataType:
            raise ValueError(
                f"Bad data type value '{data_type}'. Valid values are: {', '.join(VALID_DATA_TYPES)}"
            )

    # @root_validator
    # def validate_times(cls, values):
    #     print("**************************************")
    #     # print(values)
    #     # print("**************************************")
    #     # starttime, endtime = values["starttime"], values["endtime"]
    #     # print(starttime)
    #     # print(endtime)
    #     # if starttime > endtime:
    #     #     raise ValueError("Starttime must be before endtime.")

    @validator("elements")
    def validate_elements(cls, elements):
        for element in elements:
            if element not in VALID_ELEMENTS and len(element) != 3:
                raise ValueError(
                    f"Bad element '{element}'."
                    f"Valid values are: {', '.join(VALID_ELEMENTS)}."
                )

    @validator("id")
    def validate_id(cls, id):
        if id not in VALID_OBSERVATORIES:
            raise ValueError(
                f"Bad observatory id '{id}'."
                f" Valid values are: {', '.join(VALID_OBSERVATORIES)}."
            )


def format_error(status_code, exception, format, request):
    if format == "json":

        error = JSONResponse(json_error(status_code, exception, request.url))

    else:
        error = Response(
            iaga2002_error(status_code, exception, request.url), media_type="text/plain"
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
        starttime=query.starttime,
        endtime=query.endtime,
        observatory=query.id,
        channels=query.elements,
        type=query.data_type,
        interval=get_interval_from_delta(query.sampling_period),
    )
    return timeseries


def iaga2002_error(code, error, url):
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


def json_error(code: int, error: Exception, url):
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
    id: str = Query(None),
    starttime: Any = Query(None),
    endtime: Any = Query(None),
    elements: List[str] = Query(DEFAULT_ELEMENTS),
    sampling_period: SamplingPeriod = Query(DEFAULT_SAMPLING_PERIOD),
    data_type: Union[DataType, str] = Query(DEFAULT_DATA_TYPE),
    format: OutputFormat = Query(DEFAULT_OUTPUT_FORMAT),
) -> WebServiceQuery:

    if len(elements) == 0:
        elements = DEFAULT_ELEMENTS
    if len(elements) == 1 and "," in elements[0]:
        elements = [e.strip() for e in elements[0].split(",")]

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
    print(type(id))
    params = WebServiceQuery(
        id=id,
        starttime=starttime,
        endtime=endtime,
        elements=elements,
        sampling_period=sampling_period,
        data_type=data_type,
        format=format,
    )
    print(params)
    params.id = id
    params.elements = elements
    params.data_type = data_type
    print("***********")
    print(params)

    return params


def validate_query(query):

    # validate combinations
    if len(query.elements) > 4 and query.format == "iaga2002":
        raise ValueError("No more than four elements allowed for iaga2002 format.")

    # check data volume
    samples = int(
        len(query.elements) * (query.endtime - query.starttime) / query.sampling_period
    )
    if samples > REQUEST_LIMIT:
        raise ValueError(f"Query exceeds request limit ({samples} > 345600)")


@app.exception_handler(ValueError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    data_format = str(request.query_params["format"])
    return format_error(400, str(exc), data_format, request)


@app.get("/data/")
def get_data(request: Request, query: WebServiceQuery = Depends(parse_query)):
    try:
        timeseries = get_timeseries(query)
        return format_timeseries(timeseries, query)
    except Exception as e:
        return format_error(500, e, query.format, request)
