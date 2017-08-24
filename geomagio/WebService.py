"""WSGI implementation of Intermagnet Web Service
"""

from __future__ import print_function
from cgi import parse_qs, escape
from datetime import datetime
import sys

from geomagio.edge import EdgeFactory
from geomagio.iaga2002 import IAGA2002Writer
from geomagio.ObservatoryMetadata import ObservatoryMetadata
from obspy.core import UTCDateTime


DEFAULT_DATA_TYPE = 'variation'
DEFAULT_ELEMENTS = ('X', 'Y', 'Z', 'F')
DEFAULT_OUTPUT_FORMAT = 'iaga2002'
DEFAULT_SAMPLING_PERIOD = '60'
VALID_DATA_TYPES = [
        'variation',
        'adjusted',
        'quasi-definitive',
        'definitive'
]
VALID_OUTPUT_FORMATS = ['iaga2002']
VALID_SAMPLING_PERIODS = ['1', '60']


def _get_param(params, key, required=False):
    """Get parameter from dictionary.

    Parameters
    ----------
    params : dict
        parameters dictionary.
    key : str
        parameter name.
    required : bool
        if required parameter.

    Returns
    -------
    value : str
        value from dictionary.

    Raises
    ------
    WebServiceError
        if the parameter is specified more than once
        or if required paramenter is not specified.
    """
    value = params.get(key)
    if type(value) in (list, tuple):
        if len(value) > 1:
            raise WebServiceException('"' + key +
                    '" may only be specified once.')
        value = escape(value[0])
    if value is None:
        if required:
            raise WebServiceException('"' + key +
                    '" is a required parameter.')
    return value


def _verify_parameters(query):
    """Verify that parameters are valid.

    Parameters
    ----------
    query : WebServiceQuery
        parsed query object.

    Raises
    ------
    WebServiceError
        if any parameters are not supported.
    """
    if len(query.elements) > 4 and query.output_format == 'iaga2002':
        raise WebServiceException(
                'No more than 4 elements allowed for iaga2002 format.')
    if query.starttime > query.endtime:
        raise WebServiceException(
                'Starttime must be before endtime.')
    if query.data_type not in VALID_DATA_TYPES:
        raise WebServiceException(
                'Bad type value "%s".'
                ' Valid values are: %s' % (query.data_type, VALID_DATA_TYPES))
    if query.sampling_period not in VALID_SAMPLING_PERIODS:
        raise WebServiceException(
                'Bad sampling_period value "%s".'
                ' Valid values are: %s'
                % (query.sampling_period, VALID_SAMPLING_PERIODS))
    if query.output_format not in VALID_OUTPUT_FORMATS:
        raise WebServiceException(
                'Bad format value "%s".'
                ' Valid values are: %s'
                % (query.output_format, VALID_OUTPUT_FORMATS))


class WebService(object):
    def __init__(self, factory, metadata=None):
        self.factory = factory
        self.metadata = metadata or ObservatoryMetadata().metadata

    def __call__(self, environ, start_response):
        """Implement WSGI interface"""
        try:
            # parse params
            query = self.parse(parse_qs(environ['QUERY_STRING']))
            # fetch data
            data = self.fetch(query)
            # format data
            data_string = self.format_data(query, data)
            if isinstance(data_string, str):
                data_string = data_string.encode('utf8')
        except Exception:
            exception = sys.exc_info()[1]
            message = exception.args[0]
            error = WebServiceError('BAD_REQUEST', message, environ)
            start_response(error.status,
                    [
                        ("Content-Type", "text/plain")
                    ])
            return [error.error_body]
        # send response
        start_response('200 OK',
                [
                    ("Content-Type", "text/plain")
                ])
        return [data_string]

    def fetch(self, query):
        """Get requested data.

        Parameters
        ----------
        query : dictionary of parsed query parameters

        Returns
        -------
        obspy.core.Stream
            timeseries object with requested data.
        """
        _verify_parameters(query)
        if query.sampling_period == '1':
            query.sampling_period = 'second'
        if query.sampling_period == '60':
            query.sampling_period = 'minute'
        data = self.factory.get_timeseries(
                observatory=query.observatory_id,
                channels=query.elements,
                starttime=query.starttime,
                endtime=query.endtime,
                type=query.data_type,
                interval=query.sampling_period)
        return data

    def format_data(self, query, data):
        """Format requested data.

        Parameters
        ----------
        query : dictionary of parsed query parameters
        data : obspy.core.Stream
            timeseries object with data to be written

        Returns
        -------
        unicode
          IAGA2002 formatted string.
        """
        # TODO: Add option for json format
        data_string = IAGA2002Writer.format(data, query.elements)
        return data_string

    def parse(self, params):
        """Parse query string parameters and set defaults.

        Parameters
        ----------
        params : dictionary
            parameters dictionary.

        Returns
        -------
        WebServiceQuery
            parsed query object.

        Raises
        ------
        WebServiceError
            if any parameters are not supported.
        """
        # Get values
        observatory_id = _get_param(params, 'id', required=True)
        starttime = _get_param(params, 'starttime')
        endtime = _get_param(params, 'endtime')
        elements = _get_param(params, 'elements')
        sampling_period = _get_param(params, 'sampling_period')
        data_type = _get_param(params, 'type')
        output_format = _get_param(params, 'format')
        # Assign values or defaults
        if not output_format:
            output_format = DEFAULT_OUTPUT_FORMAT
        else:
            output_format = output_format.lower()
        observatory_id = observatory_id.upper()
        if observatory_id not in self.metadata.keys():
            raise WebServiceException(
                   'Bad id value "%s".'
                   ' Valid values are: %s'
                   % (observatory_id, self.metadata.keys()))
        if not starttime:
            now = datetime.now()
            today = UTCDateTime(
                    year=now.year,
                    month=now.month,
                    day=now.day,
                    hour=0)
            starttime = today
        else:
            try:
                starttime = UTCDateTime(starttime)
            except:
                raise WebServiceException(
                        'Bad starttime value "%s".'
                        ' Valid values are ISO-8601 timestamps.' % starttime)
        if not endtime:
            endtime = starttime + (24 * 60 * 60 - 1)
        else:
            try:
                endtime = UTCDateTime(endtime)
            except:
                raise WebServiceException(
                        'Bad endtime value "%s".'
                        ' Valid values are ISO-8601 timestamps.' % endtime)
        if not elements:
            elements = DEFAULT_ELEMENTS
        else:
            elements = [el.strip().upper() for el in elements.split(',')]
        if not sampling_period:
            sampling_period = DEFAULT_SAMPLING_PERIOD
        else:
            sampling_period = sampling_period
        if not data_type:
            data_type = DEFAULT_DATA_TYPE
        else:
            data_type = data_type.lower()
        # Create WebServiceQuery object and set properties
        query = WebServiceQuery
        query.observatory_id = observatory_id
        query.starttime = starttime
        query.endtime = endtime
        query.elements = elements
        query.sampling_period = sampling_period
        query.data_type = data_type
        query.output_format = output_format
        return query


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
    def __init__(self, observatory_id=None, starttime=None, endtime=None,
            elements=None, sampling_period=60, data_type='variation',
            output_format='iaga2002'):
        self.observatory_id = observatory_id
        self.starttime = starttime
        self.endtime = endtime
        self.elements = elements
        self.sampling_period = sampling_period
        self.data_type = data_type
        self.output_format = output_format


class WebServiceException(Exception):
    """Base class for exceptions thrown by web services."""
    pass


class WebServiceError(object):
    """Base class for creating error pages."""
    def __init__(self, code, message, environ):
        self.code = code
        self.message = message
        self.environ = environ
        self.error_body = None
        self.error_types = {
                'NO_DATA': {
                        'code': 204,
                        'status': 'No Data'
                },
                'BAD_REQUEST': {
                        'code': 400,
                        'status': 'Bad Request'
                },
                'NOT_FOUND': {
                        'code': 404,
                        'status': 'Not Found'
                },
                'CONFLICT': {
                        'code': 409,
                        'status': 'Conflict'
                },
                'SERVER_ERROR': {
                        'code': 500,
                        'status': 'Internal Server Error'
                },
                'NOT_IMPLEMENTED': {
                        'code': 501,
                        'status': 'Not Implemented'
                },
                'SERVICE_UNAVAILABLE': {
                        'code': 503,
                        'status': 'Service Unavailable'
                },
        }
        self.status = None
        self.error()

    def error(self):
        """Assign error_body value based on error format."""
        # TODO: Add option for json formatted error
        self.error_body = self.http_error()

    def http_error(self):
        """Format http error message.

        Returns
        -------
        error_body : str
            body of http error message.
        """
        code_message = str(self.error_types[self.code]['code'])
        status_message = self.error_types[self.code]['status']
        self.status = code_message + ' ' + status_message
        server_software = self.environ['SERVER_SOFTWARE'].split(' ')
        error_body = 'Error ' + code_message + ': ' + status_message + \
                '\n\n' + self.message + '\n\n' + \
                'Usage details are available from ' + \
                'http://geomag.usgs.gov/ws/edge/ \n\n' + \
                'Request:\n' + \
                self.environ['QUERY_STRING'] + '\n\n' + \
                'Request Submitted:\n' + \
                datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") + '\n\n' + \
                'Service version:\n' + \
                server_software[0]
        return error_body


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    app = WebService(EdgeFactory())
    httpd = make_server('', 7981, app)
    httpd.serve_forever()
