"""WSGI implementation of Intermagnet Web Service
"""

from __future__ import print_function
from cgi import parse_qs, escape
from datetime import datetime
import sys

from geomagio.edge import EdgeFactory
from geomagio.iaga2002 import IAGA2002Writer
from geomagio.ObservatoryMetadata import ObservatoryMetadata
from geomagio.WebServiceUsage import WebServiceUsage
from obspy.core import UTCDateTime


DEFAULT_DATA_TYPE = 'variation'
DEFAULT_ELEMENTS = ('X', 'Y', 'Z', 'F')
DEFAULT_OUTPUT_FORMAT = 'iaga2002'
DEFAULT_SAMPLING_PERIOD = '60'
ERROR_CODE_MESSAGES = {
        204: 'No Data',
        400: 'Bad Request',
        404: 'Not Found',
        409: 'Conflict',
        500: 'Internal Server Error',
        501: 'Not Implemented',
        503: 'Service Unavailable'
}
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
    WebServiceException
        if the parameter is specified more than once
        or if required paramenter is not specified.
    """
    value = params.get(key)
    if isinstance(value, (list, tuple)):
        if len(value) > 1:
            raise WebServiceException('"' + key +
                    '" may only be specified once.')
        value = escape(value[0])
    if value is None:
        if required:
            raise WebServiceException('"' + key +
                    '" is a required parameter.')
    return value


class WebService(object):
    def __init__(self, factory=None, version=None, metadata=None,
            usage_documentation=None):
        self.factory = factory or EdgeFactory()
        self.metadata = metadata or ObservatoryMetadata().metadata
        self.version = version
        self.usage_documentation = usage_documentation or WebServiceUsage()

    def __call__(self, environ, start_response):
        """Implement WSGI interface"""
        if environ['QUERY_STRING'] == '':
            return self.usage_documentation.__call__(environ, start_response)
        try:
            # parse params
            query = self.parse(parse_qs(environ['QUERY_STRING']))
            query._verify_parameters()
        except Exception:
            exception = sys.exc_info()[1]
            message = exception.args[0]
            error_body = self.error(400, message, environ, start_response)
            return [error_body]
        try:
            # fetch timeseries
            timeseries = self.fetch(query)
            # format timeseries
            timeseries_string = self.format_data(
                    query, timeseries, start_response)
            if isinstance(timeseries_string, str):
                timeseries_string = timeseries_string.encode('utf8')
        except Exception:
            exception = sys.exc_info()[1]
            message = exception.args[0]
            error_body = self.error(500, message, environ, start_response)
            return [error_body]
        return [timeseries_string]

    def error(self, code, message, environ, start_response):
        """Assign error_body value based on error format."""
        # TODO: Add option for json formatted error
        error_body = self.http_error(code, message, environ)
        status = str(code) + ' ' + ERROR_CODE_MESSAGES[code]
        start_response(status,
                [
                    ("Content-Type", "text/plain")
                ])
        if isinstance(error_body, str):
            error_body = error_body.encode('utf8')
        return error_body

    def fetch(self, query):
        """Get requested timeseries.

        Parameters
        ----------
        query : dictionary of parsed query parameters

        Returns
        -------
        obspy.core.Stream
            timeseries object with requested data.
        """
        if query.sampling_period == '1':
            sampling_period = 'second'
        if query.sampling_period == '60':
            sampling_period = 'minute'
        timeseries = self.factory.get_timeseries(
                observatory=query.observatory_id,
                channels=query.elements,
                starttime=query.starttime,
                endtime=query.endtime,
                type=query.data_type,
                interval=sampling_period)
        return timeseries

    def format_data(self, query, timeseries, start_response):
        """Format requested timeseries.

        Parameters
        ----------
        query : dictionary of parsed query parameters
        timeseries : obspy.core.Stream
            timeseries object with data to be written

        Returns
        -------
        unicode
          IAGA2002 formatted string.
        """
        # TODO: Add option for json format
        timeseries_string = IAGA2002Writer.format(timeseries, query.elements)
        start_response('200 OK',
                [
                    ("Content-Type", "text/plain")
                ])
        return timeseries_string

    def http_error(self, code, message, environ):
        """Format http error message.

        Returns
        -------
        error_body : str
            body of http error message.
        """
        status_message = ERROR_CODE_MESSAGES[code]
        http_error_body = 'Error ' + str(code) + ': ' + status_message + \
                '\n\n' + message + '\n\n' + \
                'Usage details are available from ' + \
                'http://geomag.usgs.gov/ws/edge/ \n\n' + \
                'Request:\n' + \
                environ['PATH_INFO'] + '?' + environ['QUERY_STRING'] + \
                '\n\n' + 'Request Submitted:\n' + \
                datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") + '\n\n'
        # Check if there is version information available
        if self.version is not None:
            http_error_body += 'Service version:\n' + str(self.version)
        return http_error_body

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
        WebServiceException
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
            except TypeError:
                raise WebServiceException(
                        'Bad starttime value "%s".'
                        ' Valid values are ISO-8601 timestamps.' % starttime)
        if not endtime:
            endtime = starttime + (24 * 60 * 60 - 1)
        else:
            try:
                endtime = UTCDateTime(endtime)
            except TypeError:
                raise WebServiceException(
                        'Bad endtime value "%s".'
                        ' Valid values are ISO-8601 timestamps.' % endtime)
        if not elements:
            elements = DEFAULT_ELEMENTS
        else:
            elements = [e.strip().upper() for e in elements.replace(',', '')]
        if not sampling_period:
            sampling_period = DEFAULT_SAMPLING_PERIOD
        else:
            sampling_period = sampling_period
        if not data_type:
            data_type = DEFAULT_DATA_TYPE
        else:
            data_type = data_type.lower()
        # Create WebServiceQuery object and set properties
        query = WebServiceQuery()
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

    def _verify_parameters(self):
        """Verify that parameters are valid.

        Raises
        ------
        WebServiceException
            if any parameters are not supported.
        """
        if len(self.elements) > 4 and self.output_format == 'iaga2002':
            raise WebServiceException(
                    'No more than four elements allowed for iaga2002 format.')
        if self.starttime > self.endtime:
            raise WebServiceException(
                    'Starttime must be before endtime.')
        if self.data_type not in VALID_DATA_TYPES:
            raise WebServiceException(
                    'Bad type value "%s".'
                    ' Valid values are: %s'
                    % (self.data_type, VALID_DATA_TYPES))
        if self.sampling_period not in VALID_SAMPLING_PERIODS:
            raise WebServiceException(
                    'Bad sampling_period value "%s".'
                    ' Valid values are: %s'
                    % (self.sampling_period, VALID_SAMPLING_PERIODS))
        if self.output_format not in VALID_OUTPUT_FORMATS:
            raise WebServiceException(
                    'Bad format value "%s".'
                    ' Valid values are: %s'
                    % (self.output_format, VALID_OUTPUT_FORMATS))


class WebServiceException(Exception):
    """Base class for exceptions thrown by web services."""
    pass
