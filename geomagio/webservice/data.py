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


DEFAULT_DATA_TYPE = 'variation'
DEFAULT_ELEMENTS = ('X', 'Y', 'Z', 'F')
DEFAULT_OUTPUT_FORMAT = 'iaga2002'
DEFAULT_SAMPLING_PERIOD = '60'
ERROR_CODE_MESSAGES = {
    204: "No Data",
    400: "Bad Request",
    404: "Not Found",
    409: "Conflict",
    500: "Internal Server Error",
    501: "Not Implemented",
    503: "Service Unavailable"
}
VALID_DATA_TYPES = ["variation", "adjusted", "quasi-definitive", "definitive"]
VALID_INTERVALS = ["tenhertz", "second", "minute", "hour", "day"]
VALID_OBSERVATORIES = ["BRT", "BRW", "DED", "DHT", "CMO", "CMT", "SIT", "SHU", "NEW",
"BDT", "BOU", "TST", "USGS", "FDT", "FRD", "FRN", "TUC", "BSL", "HON", "SJG",
"GUA", "SJT"]
VALID_OUTPUT_FORMATS = ["iaga2002", "json"]
VALID_SAMPLING_PERIODS = ["0.1", "1", "60", "3600", "86400"]


blueprint = Blueprint("data", __name__)
input_factory = None
VERSION = 'version'


def init_app(app: Flask):
    global blueprint
    global input_factory
    input_factory = get_input_factory()

    app.register_blueprint(blueprint)


@blueprint.route("/data", methods=["GET"])
def get_data():
    query_params = request.args

    if not query_params:
        return render_template("data/usage.html")

    try:
        parsed_query = parse_query(query_params)
        validate_query(parsed_query)
    except Exception as e:
        exception = str(e)
        error_body = format_error(400, exception, parsed_query, request)
        return error_body

    try:
        timeseries = get_timeseries(parsed_query)
        return format_timeseries(timeseries, parsed_query)
    except Exception as e:
        exception = str(e)
        error_body = format_error(500, exception, parsed_query, request)
        return error_body


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
        output_format="iaga2002"
    ):
        self.observatory_id = observatory_id
        self.starttime = starttime
        self.endtime = endtime
        self.elements = elements
        self.sampling_period = sampling_period
        self.data_type = data_type
        self.output_format = output_format


def format_error(status_code, exception, parsed_query, request):
    """Assign error_body value based on error format."""

    if parsed_query.output_format == 'json':
        return Response(
            json_error(status_code, exception, request.url),
            mimetype="application/json")
    else:
        return Response(
            iaga2002_error(status_code, exception, request.query_string),
            mimetype="text/plain")


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
            mimetype="application/json")
    else:
        return Response(
            IAGA2002Writer.format(timeseries, query.elements),
            mimetype="text/plain")


def get_input_factory():
    """Reads environment variable to determine the factory to be used

    Returns
    -------
    input_factory
        Edge or miniseed factory object
    """
    data_type = os.getenv('DATA_TYPE', 'edge')
    host = os.getenv('DATA_HOST', 'cwbpub.cr.usgs.gov')
    port = os.getenv('DATA_PORT', 2060)

    if data_type == 'edge':
        input_factory = EdgeFactory(
        host=host,
        port=port,
        type=data_type)
        return input_factory
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
    timeseries = input_factory.get_timeseries(
        query.starttime,
        query.endtime,
        query.observatory_id,
        query.elements,
        query.data_type,
        query.sampling_period)
    return timeseries


def iaga2002_error(code, message, request_args):
    """Format iaga2002 error message.

    Returns
    -------
    error_body : str
        body of iaga2002 error message.
    """
    status_message = ERROR_CODE_MESSAGES[code]
    error_body = f"""Error {code}: {status_message}

{message}

Usage details are available from {request.base_url}

Request:
{request.url}

Request Submitted:
{UTCDateTime().isoformat()}Z

Service Version:
{VERSION}
"""
    return error_body


def json_error(code, message, url):
    """Format json error message.

    Returns
    -------
    error_body : str
        body of json error message.
    """
    date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    status_message = ERROR_CODE_MESSAGES[code]

    error_dict = {
        "type": "Error",
        "metadata": {
            "status": code,
            "generated": date,
            "url": url,
            "title": status_message,
            "error": message
        }

    }
    return dumps(error_dict,
    sort_keys=True).encode('utf8')


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
    observatory_id = query.get("observatory")
    elements = query.get("channels", DEFAULT_ELEMENTS)
    sampling_period = query.get("sampling_period", DEFAULT_SAMPLING_PERIOD)
    data_type = query.get("type", DEFAULT_DATA_TYPE)
    output_format = query.get("format", DEFAULT_OUTPUT_FORMAT)
    # Format values and get time values
    output_format.lower()
    observatory_id.upper()

    try:
        start_time = UTCDateTime(query.get('starttime'))
    except:
        start_time = query.get('starttime')
    if not start_time:
        now = datetime.now()
        today = UTCDateTime(
                year=now.year,
                month=now.month,
                day=now.day,
                hour=0)
        start_time = today

    try:
        end_time = UTCDateTime(query.get("endtime"))
    except:
        end_time = query.get("endtime")
    if not end_time:
        end_time = start_time + (24 * 60 * 60 - 1)
        end_time = UTCDateTime(end_time)

    # Create WebServiceQuery object and set properties
    params = WebServiceQuery()
    params.observatory_id = observatory_id
    params.starttime = start_time
    params.endtime = end_time
    params.elements = elements
    params.sampling_period = get_interval_from_delta(sampling_period)
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
    if not query.endtime:
         raise WebServiceException(
                    'Bad end_time value "%s".'
                    ' Valid values are ISO-8601 timestamps.' % query.endtime)
    if type(query.starttime) == str:
         raise WebServiceException(
                    'Bad end_time value "%s".'
                    ' Valid values are ISO-8601 timestamps.' % query.starttime)
    if len(query.elements) > 4 and query.output_format == "iaga2002":
        raise WebServiceException(
            "No more than four elements allowed for iaga2002 format."
        )
    if query.observatory_id not in VALID_OBSERVATORIES:
        raise WebServiceException(
             f"""Bad observatory id "{query.observatory_id}".  Valid values are:  {', '.join(VALID_OBSERVATORIES)}."""
            )
    if query.starttime > query.endtime:
        raise WebServiceException("Starttime must be before endtime.")
    if query.data_type not in VALID_DATA_TYPES:
        raise WebServiceException(
             f"""Bad data type value "{query.data_type}". Valid values are:  {', '.join(VALID_DATA_TYPES)}."""
            )
    if query.sampling_period not in VALID_INTERVALS:
        raise WebServiceException(
            f"""Bad sampling_period value {query.sampling_period}. Valid values are:  {', '.join(VALID_SAMPLING_PERIODS)}."""
            )
    if query.output_format not in VALID_OUTPUT_FORMATS:
        raise WebServiceException(
             f"""Bad format value "{query.output_format}".  Valid values are:  {', '.join(VALID_OUTPUT_FORMATS)}."""
            )