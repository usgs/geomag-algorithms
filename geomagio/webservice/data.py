from datetime import datetime
import os
from flask import Blueprint, Flask, jsonify, render_template, request, Response
from obspy import UTCDateTime
from collections import OrderedDict
from json import dumps

from geomagio.edge import EdgeFactory
from geomagio.iaga2002 import IAGA2002Writer
from geomagio.imfjson import IMFJSONWriter

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
VALID_OUTPUT_FORMATS = ["iaga2002", "json"]
VALID_SAMPLING_PERIODS = ["1", "60"]

blueprint = Blueprint("data", __name__)
factory = EdgeFactory(
    host=os.getenv('host', 'cwbpub.cr.usgs.gov'),
    port=os.getenv('port', 2060),
    write_port=os.getenv('write_port', 7981)
   )

def init_app(app: Flask):
    global blueprint
    global factory

    app.register_blueprint(blueprint)

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

    def _verify_parameters(self):
        """Verify that parameters are valid.
        Raises
        ------
        WebServiceException
            if any parameters are not supported.
        """
        if len(self.elements) > 4 and self.output_format == "iaga2002":
            raise WebServiceException(
                "No more than four elements allowed for iaga2002 format."
            )
        if self.starttime > self.endtime:
            raise WebServiceException("Starttime must be before endtime.")
        if self.data_type not in VALID_DATA_TYPES:
            raise WebServiceException(
                'Bad type value "%s".'
                " Valid values are: %s" % (self.data_type, VALID_DATA_TYPES)
            )
        if self.sampling_period not in VALID_SAMPLING_PERIODS:
            raise WebServiceException(
                'Bad sampling_period value "%s".'
                " Valid values are: %s" % (self.sampling_period, VALID_SAMPLING_PERIODS)
            )
        if self.output_format not in VALID_OUTPUT_FORMATS:
            raise WebServiceException(
                'Bad format value "%s".'
                " Valid values are: %s" % (self.output_format, VALID_OUTPUT_FORMATS)
            )

@blueprint.route("/data", methods=["GET"])
def get_data():
    query_params = request.args

    url = request.url

    if not query_params:
        return render_template("usage.html")

    parsed_query = parse_query(query_params)

    try:
        parsed_query._verify_parameters()
    except Exception as e:
        message = str(e)
        error_body = error(400, message, parsed_query, url)
        return error_body

    try:
        timeseries = get_timeseries(parsed_query)
    except Exception as e:
        message = str(e)
        error_body = error(500, message, parsed_query, url)
        return error_body

    return format_timeseries(timeseries, parsed_query)

def error(code, message, query, url):
    error_body = http_error(code, message, query, url)
    status = str(code) + ' ' + ERROR_CODE_MESSAGES[code]

    Response(error_body, mimetype="text/plain")

    return error_body

def http_error(code, message, query, url):
    if query.output_format == 'json':
        http_error_body = json_error(code, message, url)
        return http_error_body
    else:
        http_error_body = iaga2002_error(code, message, url)
        return http_error_body

def json_error(code, message, url):
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

def iaga2002_error(code, message, url):
    status_message = ERROR_CODE_MESSAGES[code]
    error_body = 'Error ' + str(code) + ': ' \
    + status_message + '\n\n' + message + '\n\n'\
    + 'Usage details are available from '\
    + 'http://geomag.usgs.gov/ws/edge/ \n\n'\
    + 'Request:\n' + url + '\n\n' + 'Request Submitted:\n'\
    + datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") + '\n'

    error_body = Response(error_body, mimetype="text/plain")
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
    if not query.get("endtime"):
        now = datetime.now()
        today = UTCDateTime(now.year, now.month, now.day, 0)
        end_time = today
    else:
        end_time = UTCDateTime(query.get("endtime"))

    if not query.get("starttime"):
        start_time = UTCDateTime(query.get("endtime")) - (24 * 60 * 60 - 1)
    else:
        start_time = UTCDateTime(query.get("starttime"))

    if query.get("sampling_period"):
        sampling_period = query.get("sampling_period")
        params.sampling_period =  sampling_period

    if query.get("format"):
        format = query.get("format")
        params.output_format = format

    observatory = query.get("observatory")

    if query.get("channels"):
        channels = query.get("channels").split(",")
        params.elements = channels

    if query.get("type"):
        type = query.get("type")
        params.data_type = type

    params.observatory_id = observatory
    params.starttime = start_time
    params.endtime = end_time

    return params

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
    if query.sampling_period == "1":
        query.sampling_period = "second"

    if query.sampling_period == "60":
        query.sampling_period = "minute"

    timeseries = factory.get_timeseries(
        query.starttime,
        query.endtime,
        query.observatory_id,
        query.elements,
        query.data_type,
        query.sampling_period)

    return timeseries

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
        json_output = IMFJSONWriter.format(timeseries, query.elements)
        json_output = Response(json_output, mimetype="application/json")

        return json_output

    else:
        iaga_output = IAGA2002Writer.format(timeseries, query.elements)
        iaga_output = Response(iaga_output, mimetype="text/plain")

        return iaga_output

class WebServiceException(Exception):
    """Base class for exceptions thrown by web services."""
    pass
