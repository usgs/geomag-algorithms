"""Unit Tests for WebService"""
from urllib.parse import parse_qs
from datetime import datetime
from numpy.testing import assert_equal, assert_raises
import numpy
import webtest

from geomagio.WebService import _get_param
from geomagio.WebService import WebService
import obspy.core
from obspy.core.stream import Stream
from obspy.core.utcdatetime import UTCDateTime


class TestFactory(object):
    "Factory to test for 200 and 400 response statuses."
    @staticmethod
    def get_timeseries(observatory=None, channels=None,
            starttime=None, endtime=None, type=None,
            interval=None):
        stream = obspy.core.Stream()
        for channel in channels:
            stats = obspy.core.Stats()
            stats.channel = channel
            stats.starttime = starttime
            stats.network = 'Test'
            stats.station = observatory
            stats.location = observatory
            if interval == 'second':
                stats.sampling_rate = 1.
            elif interval == 'minute':
                stats.sampling_rate = 1. / 60.
            elif interval == 'hourly':
                stats.sampling_rate = 1. / 3600.
            elif interval == 'daily':
                stats.sampling_rate = 1. / 86400.
            length = int((endtime - starttime) * stats.sampling_rate)
            stats.npts = length + 1
            data = numpy.full(length, numpy.nan, dtype=numpy.float64)
            trace = obspy.core.Trace(data, stats)
            stream.append(trace)
        return stream


class ErrorFactory(object):
    "Factory to test for 500 response status."
    @staticmethod
    def get_timeseries(observatory=None, channels=None,
            starttime=None, endtime=None, type=None,
            interval=None):
        pass


def test__get_param():
    """WebService_test.test__get_param()

    Call function _get_param to make certain it gets back
    the appropriate values and raises exceptions for invalid values.
    """
    params = {
        'id': None,
        'elements': 'H,E,Z,F',
        'sampling_period': ['1', '60'],
    }
    assert_raises(Exception, _get_param, params, 'id', required=True)
    elements = _get_param(params, 'elements')
    assert_equal(elements, 'H,E,Z,F')
    assert_raises(Exception, _get_param, params, 'sampling_period')


def test_fetch():
    """WebService_test.test_fetch())

    Call function WebService.fetch to confirm tht it returns an
    obspy.core.stream object.
    """
    service = WebService(TestFactory())
    query = service.parse(parse_qs('id=BOU&starttime=2016-06-06'
            '&endtime=2016-06-07&elements=H,E,Z,F&sampling_period=60'
            '&format=iaga2002&type=variation'))
    timeseries = service.fetch(query)
    assert_equal(isinstance(timeseries, Stream), True)


def test_parse():
    """WebService_test.test_parse()

    Create WebService instance and call parse to confirm that query
    string values are applied to the correct class attribute. Also
    confirm that default values are applied correctly.
    """
    service = WebService(TestFactory())
    query = service.parse(parse_qs('id=BOU&starttime=2016-06-06'
            '&endtime=2016-06-07&elements=H,E,Z,F&sampling_period=60'
            '&format=iaga2002&type=variation'))
    assert_equal(query.observatory_id, 'BOU')
    assert_equal(query.starttime, UTCDateTime(2016, 6, 6, 0))
    assert_equal(query.endtime, UTCDateTime(2016, 6, 7, 0))
    assert_equal(query.elements, ['H', 'E', 'Z', 'F'])
    assert_equal(query.sampling_period, '60')
    assert_equal(query.output_format, 'iaga2002')
    assert_equal(query.data_type, 'variation')
    # Test that defaults are set for unspecified values
    now = datetime.now()
    today = UTCDateTime(year=now.year, month=now.month, day=now.day, hour=0)
    tomorrow = today + (24 * 60 * 60 - 1)
    query = service.parse(parse_qs('id=BOU'))
    assert_equal(query.observatory_id, 'BOU')
    assert_equal(query.starttime, today)
    assert_equal(query.endtime, tomorrow)
    assert_equal(query.elements, ('X', 'Y', 'Z', 'F'))
    assert_equal(query.sampling_period, '60')
    assert_equal(query.output_format, 'iaga2002')
    assert_equal(query.data_type, 'variation')
    assert_raises(Exception, service.parse, parse_qs('/?id=bad'))


def test_requests():
    """WebService_test.test_requests()

    Use TestApp to confirm correct response status, status int,
    and content-type.
    """
    app = webtest.TestApp(WebService(TestFactory()))
    # Check invalid request (bad values)
    response = app.get('/?id=bad', expect_errors=True)
    assert_equal(response.status_int, 400)
    assert_equal(response.status, '400 Bad Request')
    assert_equal(response.content_type, 'text/plain')
    # Check invalid request (duplicates)
    response = app.get('/?id=BOU&id=BOU', expect_errors=True)
    assert_equal(response.status_int, 400)
    assert_equal(response.status, '400 Bad Request')
    assert_equal(response.content_type, 'text/plain')
    # Check valid request (upper and lower case)
    response = app.get('/?id=BOU')
    assert_equal(response.status_int, 200)
    assert_equal(response.status, '200 OK')
    assert_equal(response.content_type, 'text/plain')
    # Test internal server error (use fake factory)
    app = webtest.TestApp(WebService(ErrorFactory(), error_stream=None))
    response = app.get('/?id=BOU', expect_errors=True)
    assert_equal(response.status_int, 500)
    assert_equal(response.status, '500 Internal Server Error')
    assert_equal(response.content_type, 'text/plain')
