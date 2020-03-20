from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from obspy import UTCDateTime
from typing import List, Any
from datetime import datetime

from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from flask.json import dumps


app = FastAPI()

DEFAULT_DATA_TYPE = "variation"
DEFAULT_ELEMENTS = ["X", "Y", "Z", "F"]
DEFAULT_OUTPUT_FORMAT = "iaga2002"
DEFAULT_SAMPLING_PERIOD = "60"
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


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/data/")
async def read_query(
    id: str,
    starttime: Any = Query(UTCDateTime(datetime.now())),
    endtime: str = Query(None),
    elements: List[str] = Query(DEFAULT_ELEMENTS),
    sampling_period: float = DEFAULT_SAMPLING_PERIOD,
    data_type: str = DEFAULT_DATA_TYPE,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
):
    starttime = UTCDateTime(starttime)
    if len(elements) == 1 and "," in elements[0]:
        elements = [e.strip() for e in elements[0].split(",")]

    observatory = {
        "observatory_id": id,
        "starttime": starttime,
        "endtime": endtime,
        "elements": elements,
        "sampling_period": sampling_period,
        "data_type": data_type,
        "output_format": output_format,
    }

    try:
        parsed_query = parse_query(observatory)
        validate_query(parsed_query)
    except Exception as e:
        return format_error(400, e)

    return parsed_query


def format_error(status_code, exception):
    return JSONResponse(json_error(status_code, exception), mimetype="application/json")


def json_error(code: int, error: Exception):
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
            "status": code,
            "generated": UTCDateTime().isoformat() + "Z",
            "url": "url",
            "title": status_message,
            "error": str(error),
        },
    }
    return dumps(error_dict, sort_keys=True).encode("utf8")


def parse_query(query):

    if not query["endtime"]:
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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)
