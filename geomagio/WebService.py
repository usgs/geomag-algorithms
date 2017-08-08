"""WSGI implementation of Intermagnet Web Service
"""

from __future__ import print_function
from builtins import str
from cgi import parse_qs, escape
from datetime import datetime

from geomagio.edge import EdgeFactory
from geomagio.iaga2002 import IAGA2002Writer
from obspy.core import UTCDateTime


DEFAULT_ELEMENTS = ('X', 'Y', 'Z', 'F')
DEFAULT_PERIOD = '60'
DEFAULT_TYPE = 'variation'
VALID_TYPES = [
        'variation',
        'adjusted',
        'quasi-definitive',
        'definitive'
]
VALID_PERIODS = ['1', '60']
VALID_FORMATS = ['iaga2002']


class WebService(object):
    def __init__(self, factory):
        self.factory = factory

    def __call__(self, environ, start_response):
        """Implement WSGI interface"""
        # parse params
        query = WebServiceQuery.parse(environ['QUERY_STRING'])
        # fetch data
        data = self.fetch(query)
        # format data
        data_string = self.format(query, data)
        if isinstance(data_string, str):
            data_string = data_string.encode('utf8')
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
        data = self.factory.get_timeseries(
                observatory=query.id,
                channels=query.elements,
                starttime=query.starttime,
                endtime=query.endtime,
                type=query.type,
                interval=query.sampling_period)
        return data

    def format(self, query, data):
        """Format requested data.

        Parameters
        ----------
        query : dictionary of parsed query parameters
        data : obspy.core.Stream
            timeseries object with data to be written

        Returns
        -------
        unicode
          IMFJSON or IAGA2002 formatted string.
        """
        # TODO: Add option for json format
        data_string = IAGA2002Writer.format(data, query.elements)
        return data_string


class WebServiceQuery(object):
    """Query parameters for a web service request.

    Parameters
    ----------
    id : str
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
    type : {'variation', 'adjusted', 'quasi-definitive', 'definitive'}
        data type
        default 'variation'.
    format : {'iaga2002', 'json'}
        output format.
        default 'iaga2002'.
    """
    def __init__(self, id=None, starttime=None, endtime=None, elements=None,
            sampling_period=60, type='variation', format='iaga2002'):
        self.id = id
        self.starttime = starttime
        self.endtime = endtime
        self.elements = elements
        self.sampling_period = sampling_period
        self.type = type
        self.format = format

    @classmethod
    def parse(cls, params):
        """Parse query string parameters and set defaults.

        Parameters
        ----------
        params : query string

        Returns
        -------
        WebServiceQuery
            parsed query object.

        Raises
        ------
        TimeseriesFactoryException
            if id, type, sampling_period, or format are not supported.
        """
        # Create dictionary of lists
        dict = parse_qs(params)
        # Get values
        if len(dict.get('id', [])) <= 1:
            id = dict.get('id', [''])[0]
        else:
            raise WebServiceException(
                '"id" accepts only one value')
        if len(dict.get('starttime', [])) <= 1:
            starttime = dict.get('starttime', [''])[0]
        else:
            raise WebServiceException(
                '"starttime" accepts only one value')
        if len(dict.get('endtime', [])) <= 1:
            endtime = dict.get('endtime', [''])[0]
        else:
            raise WebServiceException(
                '"endtime" accepts only one value')
        if len(dict.get('elements', [])) <= 1:
            elements = dict.get('elements', [''])[0]
        else:
            raise WebServiceException(
                '"elements" accepts only one set of values')
        if len(dict.get('sampling_period', [])) <= 1:
            sampling_period = dict.get('sampling_period', [''])[0]
        else:
            raise WebServiceException(
                '"sampling_period" accepts only one value')
        if len(dict.get('type', [])) <= 1:
            type = dict.get('type', [''])[0]
        else:
            raise WebServiceException(
                '"type" accepts only one value')
        if len(dict.get('format', [])) <= 1:
            format = dict.get('format', [''])[0]
        else:
            raise WebServiceException(
                '"format" accepts only one value')
        # Escape to avoid script injection
        id = escape(id)
        starttime = escape(starttime)
        endtime = escape(endtime)
        elements = escape(elements)
        sampling_period = escape(sampling_period)
        type = escape(type).lower()
        format = escape(format)
        # Check for parameters and set defaults
        if not id:
            raise WebServiceException(
                '"id" is a required parameter')
        now = datetime.now()
        if starttime:
            try:
                starttime = UTCDateTime(starttime)
            except:
                raise WebServiceException(
                        'Invalid starttime "%s"' % starttime)
        else:
            starttime = UTCDateTime(
                    year=now.year,
                    month=now.month,
                    day=now.day,
                    hour=0)
        if endtime:
            try:
                endtime = UTCDateTime(endtime)
            except:
                raise WebServiceException(
                        'Invalid endtime "%s"' % endtime)
        else:
            endtime = starttime + (24 * 60 * 60 - 1)
        if starttime > endtime:
            raise WebServiceException(
                    'Starttime before endtime "%s" "%s"'
                     % (starttime, endtime))
        if elements:
            elements = [el.strip().upper() for el in elements.split(',')]
        else:
            elements = DEFAULT_ELEMENTS
        if not sampling_period:
            sampling_period = DEFAULT_PERIOD
        if sampling_period not in VALID_PERIODS:
            raise WebServiceException(
                    'Invalid sampling period.'
                    ' Valid sampling periods: %s' % VALID_PERIODS)
        # TODO: Add hourly option
        if sampling_period == '1':
            sampling_period = 'second'
        if sampling_period == '60':
            sampling_period = 'minute'
        if not type:
            type = DEFAULT_TYPE
        if type not in VALID_TYPES:
            raise WebServiceException(
                'Invalid data type.'
                ' Valid data types: %s' % VALID_TYPES)
        # TODO: Add json to valid formats
        if not format:
            format = 'iaga2002'
        if format not in VALID_FORMATS:
            raise WebServiceException(
                'Invalid format.'
                ' Valid formats: %s' % VALID_FORMATS)
        # Create WebServiceQuery object and set properties
        query = WebServiceQuery
        query.id = id
        query.starttime = starttime
        query.endtime = endtime
        query.elements = elements
        query.sampling_period = sampling_period
        query.type = type
        query.format = format
        return query


class WebServiceException(Exception):
    """Base class for exceptions thrown by web services."""
    pass


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    app = WebService(EdgeFactory())
    httpd = make_server('', 8080, app)
    httpd.serve_forever()
