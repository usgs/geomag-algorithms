"""WSGI implementation of Intermagnet Web Service
"""

from __future__ import print_function
from builtins import str
from cgi import parse_qs, escape
from datetime import datetime

from geomagio.edge import EdgeFactory
from geomagio.iaga2002 import IAGA2002Writer
from obspy.core import UTCDateTime


class WebService(object):
    def __init__(self, factory):
        self.factory = factory

    def __call__(self, environ, start_response):
        """Implement WSGI interface"""
        # parse params
        query = {}
        query = WebServiceQuery.parse(environ['QUERY_STRING'])
        # fetch data
        data = self.fetch(query)
        # format data
        data_string = self.format(query, data)
        # send response
        start_response('200 OK',
                [
                    ("Content-Type", "text/plain")
                ])
        if isinstance(data_string, str):
            data_string = data_string.encode('utf8')
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
                observatory=query['id'],
                channels=query['elements'],
                starttime=query['starttime'],
                endtime=query['endtime'],
                type=query['type'],
                interval=query['sampling_period'])
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
        data_string = IAGA2002Writer.format(data, query['elements'])
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
        # Return values
        id = dict.get('id', [''])[0]
        starttime = dict.get('starttime', [''])[0]
        endtime = dict.get('endtime', [''])[0]
        elements = dict.get('elements', [''])[0]
        sampling_period = dict.get('sampling_period', [''])[0]
        type = dict.get('type', [''])[0]
        format = dict.get('format', [''])[0]
        # Escape to avoid script injection
        id = escape(id)
        starttime = escape(starttime)
        endtime = escape(endtime)
        elements = escape(elements)
        sampling_period = escape(sampling_period)
        type = escape(type)
        format = escape(format)
        # Check for parameters and set defaults
        if not id:
            raise WebServiceException(
                'Missing observatory id.')
        now = datetime.now()
        if starttime and endtime:
            starttime = UTCDateTime(starttime)
            endtime = UTCDateTime(endtime)
        if not starttime and not endtime:
            starttime = UTCDateTime(
                        year=now.year,
                        month=now.month,
                        day=now.day,
                        hour=0)
            endtime = starttime  + (24 * 60 * 60 - 1)
        if starttime and not endtime:
            starttime = UTCDateTime(starttime)
            endtime = starttime  + (24 * 60 * 60 - 1)
        if not starttime and endtime:
            raise WebServiceException(
                    'Missing start time.')
        if elements:
            elements = [el.strip().upper() for el in elements.split(',')]
        if not elements:
            elements = ('X', 'Y', 'Z', 'F')
        valid_periods = ['1', '60']
        if not sampling_period:
            sampling_period = '60'
        if sampling_period not in valid_periods:
            raise WebServiceException(
                    'Invalid sampling period.'\
                    ' Valid sampling periods: %s' % valid_periods)
        # TODO: Add hourly option
        if sampling_period == '1':
            sampling_period = 'second'
        if sampling_period == '60':
            sampling_period = 'minute'
        valid_types = [
                    'variation',
                    'adjusted',
                    'quasi-definitive',
                    'definitive'
                    ]
        if not type:
            type = 'variation'
        if type not in valid_types:
            raise WebServiceException(
                'Invalid data type.'\
                ' Valid data types: %s' % valid_types)
        # TODO: Add json to valid formats
        valid_formats = ['iaga2002']
        if not format:
            format = 'iaga2002'
        if format not in valid_formats:
            raise WebServiceException(
                'Invalid format.'\
                ' Valid formats: %s' % valid_formats)
        # Fill dictionary with parameters and return
        query = {}
        query['id'] = id
        query['starttime'] = starttime
        query['endtime'] = endtime
        query['elements'] = elements
        query['sampling_period'] = sampling_period
        query['type'] = type
        query['format'] = format
        return query


class WebServiceException(Exception):
    """Base class for exceptions thrown by web services."""
    pass


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    app = WebService(EdgeFactory())
    httpd = make_server('', 8080, app)
    httpd.serve_forever()
