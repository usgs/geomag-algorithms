"""WSGI implementation of Intermagnet Web Service
"""

from __future__ import print_function
from builtins import bytes, str

from geomagio.edge import EdgeFactory
from geomagio.iaga2002 import IAGA2002Writer
from obspy.core import UTCDateTime


class WebService(object):
    def __init__(self, factory):
        self.factory = factory

    def __call__(self, environ, start_response):
        """Implement WSGI interface"""
        # parse params
        # fetch data
        # send response
        start_response('200 OK',
                [
                    ("Content-Type", "text/plain")
                ])
        data = self.factory.get_timeseries(
                observatory='BOU',
                channels=('H', 'E', 'Z', 'F'),
                starttime=UTCDateTime('2017-07-14T00:00:00Z'),
                endtime=UTCDateTime('2017-07-15T00:00:00Z'),
                type='variation',
                interval='minute')
        data = IAGA2002Writer.format(data, ('H', 'E', 'Z', 'F'))
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
    def parse(params):
        """Parse query parameters from a dictionary.

        Parameters
        ----------
        params : dict

        Returns
        -------
        WebServiceQuery
            parsed query object.
        """
        pass


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    app = WebService(EdgeFactory())
    httpd = make_server('', 8080, app)
    httpd.serve_forever()
