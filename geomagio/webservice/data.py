from collections import OrderedDict
from datetime import datetime
from flask import Blueprint, Flask, jsonify, render_template, request, Response
from json import dumps
from obspy import UTCDateTime
import os

from geomagio.edge import EdgeFactory
from geomagio.iaga2002 import IAGA2002Writer
from geomagio.imfjson import IMFJSONWriter
from geomagio.TimeseriesUtility import get_interval_from_delta


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
VALID_OBSERVATORIES = ["BRT", "BRW", "DED", "DHT", "CMO", "CMT", "SIT", "SHU", "NEW",
"BDT", "BOU", "TST", "USGS", "FDT", "FRD", "FRN", "TUC", "BSL", "HON", "SJG",
"GUA", "SJT"]
VALID_OUTPUT_FORMATS = ["iaga2002", "json"]
VALID_SAMPLING_PERIODS = [0.1, 1, 60, 3600, 86400]


blueprint = Blueprint("data", __name__)


def init_app(app: Flask):
    global blueprint

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


def format_error(status_code, exception, query, url):
    """Assign error_body value based on error format."""
    error_body = http_error(status_code, exception, query, url)
    status = str(status_code) + ' ' + ERROR_CODE_MESSAGES[status_code]

    return Response(error_body, mimetype="text/plain")


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
    DATA_TYPE = os.getenv('Type', 'edge')

    if DATA_TYPE == 'edge':
        input_factory = EdgeFactory(
        host=os.getenv('DATA_HOST', 'cwbpub.cr.usgs.gov'),
        port=os.getenv('DATA_PORT', 2060)
        )
        return input_factory


def get_timeseries(query):
    """
    Parameters
    ----------
     WebServiceQuery
        parsed query object

    Returns
    -------
    obspy.core.Stream
        timeseries object with requested data
    """
    data_interval = get_interval_from_delta(query.sampling_period)
    query.sampling_period = data_interval
    print(data_interval)
    input_factory = get_input_factory()

    timeseries = input_factory.get_timeseries(
        query.starttime,
        query.endtime,
        query.observatory_id,
        query.elements,
        query.data_type,
        query.sampling_period)

    return timeseries


def http_error(code, message, query, request):
    """Format http error message.

    Returns
    -------
    http_error_body : str
        body of http error message.
    """
    if query.output_format == 'json':
        http_error_body = json_error(code, message, request.url)
        return http_error_body
    else:
        http_error_body = iaga2002_error(code, message, request.query_string)
        return http_error_body


def iaga2002_error(code, message, request_args):
    """Format iaga2002 error message.

    Returns
    -------
    error_body : str
        body of iaga2002 error message.
    """

    status_message = ERROR_CODE_MESSAGES[code]
    error_body = 'Error ' + str(code) + ': ' \
    + status_message + '\n\n' + message + '\n\n'\
    + 'Usage details are available from '\
    + 'http://geomag.usgs.gov/ws/edge/ \n\n'\
    + 'Request:\n' + 'ws/edge/?' + str(request_args)[2:-1] + '\n\n' + 'Request Submitted:\n'\
    + datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") + '\n'

    error_body = Response(error_body, mimetype="text/plain")
    return error_body


def json_error(code, message, url):
    """Format json error message.

    Returns
    -------
    error_body : str
        body of json error message.
    """
    error_dict = OrderedDict()
    error_dict['type'] = "Error"
    error_dict['metadata'] = OrderedDict()
    error_dict['metadata']['status'] = code
    date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    error_dict['metadata']['generated'] = date
    error_dict['metadata']['url'] = url
    status_message = ERROR_CODE_MESSAGES[code]
    error_dict['metadata']['title'] = status_message
    error_dict['metadata']['error'] = message
    error_body = dumps(error_dict,
    ensure_ascii=True).encode('utf8')

    return error_body


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
    # Create web service query object
    params = WebServiceQuery()

    # Get and assign values
    if not query.get("starttime"):
        start_time = UTCDateTime(query.get("endtime")) - (24 * 60 * 60 - 1)
    else:
        start_time = UTCDateTime(query.get("starttime"))
    params.starttime = start_time

    if not query.get("endtime"):
        now = datetime.now()
        today = UTCDateTime(now.year, now.month, now.day, 0)
        end_time = today
    else:
        end_time = UTCDateTime(query.get("endtime"))
    params.endtime = end_time

    if query.get("sampling_period"):
        sampling_period = int(query.get("sampling_period"))
        params.sampling_period =  sampling_period

    if query.get("format"):
        format = query.get("format")
        params.output_format = format

    observatory = query.get("observatory")
    params.observatory_id = observatory

    if query.get("channels"):
        channels = query.get("channels").split(",")
        params.elements = channels

    if query.get("type"):
        type = query.get("type")
        params.data_type = type

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
    if len(query.elements) > 4 and query.output_format == "iaga2002":
        raise WebServiceException(
            "No more than four elements allowed for iaga2002 format."
        )
    if query.observatory_id not in VALID_OBSERVATORIES:
        raise WebServiceException(
            'Bad observatory ID "%s".'
            " Valid values are: %s" % (query.observatory_id, ', '.join(VALID_OBSERVATORIES) + '.')
            )
    if query.starttime > query.endtime:
        raise WebServiceException("Starttime must be before endtime.")
    if query.data_type not in VALID_DATA_TYPES:
        raise WebServiceException(
            'Bad type value "%s".'
            " Valid values are: %s" % (query.data_type, ', '.join(VALID_DATA_TYPES) + '.')
            )
    if query.sampling_period not in VALID_SAMPLING_PERIODS:
        raise WebServiceException(
            'Bad sampling_period value "%s".'
            " Valid values are: %s" % (query.sampling_period, ', '.join(VALID_SAMPLING_PERIODS) + '.')
            )
    if query.output_format not in VALID_OUTPUT_FORMATS:
        raise WebServiceException(
            'Bad format value "%s".'
            " Valid values are: %s" % (query.output_format, ', '.join(VALID_OUTPUT_FORMATS) + '.')
            )