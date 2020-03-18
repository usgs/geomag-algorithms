from collections import OrderedDict
from datetime import datetime
from flask import Blueprint, Flask, jsonify, render_template, request, Response
from json import dumps
from obspy import UTCDateTime
import os

from ..edge import EdgeFactory
from ..iaga2002 import IAGA2002Writer
from ..imfjson import IMFJSONWriter
from ..TimeseriesUtility import get_interval_from_delta


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


blueprint = Blueprint("data", __name__)
data_factory = None
VERSION = "version"


def init_app(app: Flask):
    global blueprint
    global data_factory
    # set up data factory
    data_factory = get_data_factory()
    app.register_blueprint(blueprint)


@blueprint.route("/data/", methods=["GET"])
def get_data():
    query_params = request.args
    if not query_params:
        return render_template(
            "data/usage.html",
            valid_data_types=VALID_DATA_TYPES,
            valid_elements=VALID_ELEMENTS,
            valid_observatories=VALID_OBSERVATORIES,
            valid_sampling_periods=VALID_SAMPLING_PERIODS,
        )
    try:
        parsed_query = parse_query(query_params)
        validate_query(parsed_query)
    except Exception as e:
        return format_error(400, e)
    try:
        timeseries = get_timeseries(parsed_query)
        return format_timeseries(timeseries, parsed_query)
    except Exception as e:
        return format_error(500, e)


class WebServiceException(Exception):
    """Base class for exceptions thrown by web services."""

    pass


class WebServiceQuery(object):
    """Query parameters for a web service request.
    Parameters
    ----------
    observatory_id : str
        observatory
    starttime : obspy.core.UTCDateTime
        time of first requested sample
    endtime : obspy.core.UTCDateTime
        time of last requested sample
    elements : array_like
        list of requested elements
    sampling_period : int
        period between samples in seconds
        default 60.
    data_type : {'variation', 'adjusted', 'quasi-definitive', 'definitive'}
        data type
        default 'variation'.
    output_format : {'iaga2002', 'json'}
        output format.
        default 'iaga2002'.
    """

    def __init__(
        self,
        observatory_id=None,
        starttime=None,
        endtime=None,
        elements=("X", "Y", "Z", "F"),
        sampling_period=60,
        data_type="variation",
        output_format="iaga2002",
    ):
        self.observatory_id = observatory_id
        self.starttime = starttime
        self.endtime = endtime
        self.elements = elements
        self.sampling_period = sampling_period
        self.data_type = data_type
        self.output_format = output_format


def format_error(status_code, exception):
    """Assign error_body value based on error format."""
    if request.args.get("format") == "json":
        return Response(json_error(status_code, exception), mimetype="application/json")
    else:
        return Response(iaga2002_error(status_code, exception), mimetype="text/plain")


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
            mimetype="application/json",
        )
    else:
        return Response(
            IAGA2002Writer.format(timeseries, query.elements), mimetype="text/plain",
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
    timeseries = data_factory.get_timeseries(
        query.starttime,
        query.endtime,
        query.observatory_id,
        query.elements,
        query.data_type,
        get_interval_from_delta(query.sampling_period),
    )
    return timeseries


def iaga2002_error(code: int, error: Exception):
    """Format iaga2002 error message.

    Returns
    -------
    error_body : str
        body of iaga2002 error message.
    """
    status_message = ERROR_CODE_MESSAGES[code]
    error_body = f"""Error {code}: {status_message}

{error}

Usage details are available from {request.base_url}

Request:
{request.url}

Request Submitted:
{UTCDateTime().isoformat()}Z

Service Version:
{VERSION}
"""
    return error_body


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
            "url": request.url,
            "title": status_message,
            "error": str(error),
        },
    }
    return dumps(error_dict, sort_keys=True).encode("utf8")


def parse_query(query):
    """Parse request arguments into a set of parameters

    Parameters
    ----------
    query: Immutable Dict
        request.args object

    Returns
    -------
    WebServiceQuery
        parsed query object

    Raises
    ------
    WebServiceException
        if any parameters are not supported.
    """
    # Get values
    observatory_id = query.get("id")
    starttime = query.get("starttime")
    endtime = query.get("endtime")
    elements = query.getlist("elements")
    sampling_period = query.get("sampling_period", DEFAULT_SAMPLING_PERIOD)
    data_type = query.get("type", DEFAULT_DATA_TYPE)
    output_format = query.get("format", DEFAULT_OUTPUT_FORMAT)
    # Parse values and set defaults
    if len(elements) == 0:
        elements = DEFAULT_ELEMENTS
    if len(elements) == 1 and "," in elements[0]:
        elements = [e.strip() for e in elements[0].split(",")]
    if not starttime:
        now = datetime.now()
        starttime = UTCDateTime(year=now.year, month=now.month, day=now.day)
    else:
        try:
            starttime = UTCDateTime(starttime)
        except Exception as e:
            raise WebServiceException(
                f"Bad starttime value '{starttime}'."
                " Valid values are ISO-8601 timestamps."
            ) from e
    if not endtime:
        endtime = starttime + (24 * 60 * 60 - 1)
    else:
        try:
            endtime = UTCDateTime(endtime)
        except Exception as e:
            raise WebServiceException(
                f"Bad endtime value '{endtime}'."
                " Valid values are ISO-8601 timestamps."
            ) from e
    try:
        sampling_period = float(sampling_period)
    except ValueError as e:
        raise WebServiceException(
            f"Bad sampling_period {sampling_period}"
            ", valid values are {','.join(VALID_SAMPLING_PERIODS)}"
        ) from e
    # Create WebServiceQuery object and set properties
    params = WebServiceQuery()
    params.observatory_id = observatory_id
    params.starttime = starttime
    params.endtime = endtime
    params.elements = elements
    params.sampling_period = sampling_period
    params.data_type = data_type
    params.output_format = output_format
    return params


def validate_query(query):
    """Verify that parameters are valid.

    Parameters
    ----------
    query: Immutable Dict
        request.args object

    Raises
    ------
    WebServiceException
        if any parameters are not supported.
    """
    # validate enumerated
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
