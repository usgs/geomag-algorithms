"""WSGI implementation of Intermagnet Web Service
"""

from __future__ import print_function
from builtins import bytes, str
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
        self.query = WebServiceQuery
        # parse params
        self.query.parse(environ['QUERY_STRING'])
        # fetch data
        data = self.query.fetch(self.factory)
        # send response
        start_response('200 OK',
                [
                    ("Content-Type", "text/plain")
                ])
        if isinstance(data, str):
            data = data.encode('utf8')
        return [data]


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
    def parse(self, params):
        """Parse query parameters from a dictionary and set defaults.

        Parameters
        ----------
        params : dict

        Returns
        -------
        WebServiceQuery
            parsed query object.
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
        self.id = escape(id)
        self.starttime = escape(starttime)
        self.endtime = escape(endtime)
        elements = escape(elements)
        self.sampling_period = escape(sampling_period)
        self.type = escape(type)
        self.format = escape(format)
        # Check for values
        if not self.id:
            self.id = 'BOU'
        if not starttime or not endtime:
            self.starttime = str(datetime.utcnow().strftime("%Y-%m-%dT")) + '00:00:00Z'
            self.endtime = str(datetime.utcnow().strftime("%Y-%m-%dT")) + '23:59:00Z'
        if elements:
            self.elements = [el.strip() and el.upper() for el in elements.split(',')]
        else:
            self.elements = ('X','Y','Z','F')
        if self.sampling_period == '1':
            self.sampling_period = 'second'
        if self.sampling_period == '60':
            self.sampling_period = 'minute'
        # TODO: Add hourly option
        if not self.sampling_period:
            self.sampling_period = 'minute'
        if not self.type:
            self.type = 'variation'
        if not self.format:
             self.format = 'iaga2002'




    @classmethod
    def fetch(self, factory):
        """Get requested data.

        Parameters
        ----------
        factory : EdgeFactory

        Returns
        -------
        data
            string of timeseries data and metadata.
        """
        self.factory = factory
        data = self.factory.get_timeseries(
                observatory=self.id,
                channels=self.elements,
                starttime=UTCDateTime(self.starttime),
                endtime=UTCDateTime(self.endtime),
                type=self.type,
                interval=self.sampling_period)
        # TODO: Add option for json and create writer
        # TODO: Add web service info (request, submission date/time, url, version)
        data = IAGA2002Writer.format(data, self.elements)
        return data

    # TODO: Add error messages and direction to usage details



if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    app = WebService(EdgeFactory())
    httpd = make_server('', 8080, app)
    httpd.serve_forever()
