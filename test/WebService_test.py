"""Unit Tests for WebService"""
from cgi import parse_qs
from datetime import datetime
from nose.tools import assert_equals
from nose.tools import assert_raises
from nose.tools import assert_is_instance
import sys
from webtest import TestApp

from geomagio.edge import EdgeFactory
from geomagio.WebService import _get_param
from geomagio.WebService import WebService
from obspy.core.stream import Stream
from obspy.core.utcdatetime import UTCDateTime


APP = TestApp(WebService(EdgeFactory()))


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
    assert_equals(elements, 'H,E,Z,F')
    assert_raises(Exception, _get_param, params, 'sampling_period')


def test_fetch():
    """WebService_test.test_fetch())

    Call function WebService.fetch to confirm tht it returns an
    obspy.core.stream object.
    """
    service = WebService(EdgeFactory())
    query = service.parse(parse_qs('id=BOU&starttime=2016-06-06'
            '&endtime=2016-06-07&elements=H,E,Z,F&sampling_period=60'
            '&format=iaga2002&type=variation'))
    timeseries = service.fetch(query)
    assert_is_instance(timeseries, Stream)


def test_parse():
    """WebService_test.test_parse()

    Create WebService instance and call parse to confirm that query
    string values are applied to the correct class attribute. Also
    confirm that default values are applied correctly.
    """
    service = WebService(EdgeFactory())
    query = service.parse(parse_qs('id=BOU&starttime=2016-06-06'
            '&endtime=2016-06-07&elements=H,E,Z,F&sampling_period=60'
            '&format=iaga2002&type=variation'))
    assert_equals(query.observatory_id, 'BOU')
    assert_equals(query.starttime, UTCDateTime(2016, 6, 6, 0))
    assert_equals(query.endtime, UTCDateTime(2016, 6, 7, 0))
    assert_equals(query.elements, ['H', 'E', 'Z', 'F'])
    assert_equals(query.sampling_period, '60')
    assert_equals(query.output_format, 'iaga2002')
    assert_equals(query.data_type, 'variation')
    # Test that defaults are set for unspecified values
    now = datetime.now()
    today = UTCDateTime(year=now.year, month=now.month, day=now.day, hour=0)
    tomorrow = today + (24 * 60 * 60 - 1)
    query = service.parse(parse_qs('id=BOU'))
    assert_equals(query.observatory_id, 'BOU')
    assert_equals(query.starttime, today)
    assert_equals(query.endtime, tomorrow)
    assert_equals(query.elements, ('X', 'Y', 'Z', 'F'))
    assert_equals(query.sampling_period, '60')
    assert_equals(query.output_format, 'iaga2002')
    assert_equals(query.data_type, 'variation')


def test_requests():
    """WebService_test.test_requests()

    Use TestApp to confirm correct response status, status int,
    and content-type.
    """
    # Check invalid request (bad values)
    invalid_values = [
        '/',
        '/?id=bad',
        '/?id=BOU&starttime=2017-50-50',
        '/?id=BOU&starttime=2016-06-06&endtime=2017-50-50',
        '/?id=BOU&starttime=2016-06-06&endtime=2016-06-05',
        '/?id=BOU&elements=H,E,D,Z,F',
        '/?id=BOU&sampling_period=20',
        '/?id=BOU&type=bad',
        '/?id=BOU&format=bad'
    ]
    for invalid_val in invalid_values:
        try:
            response = APP.get(invalid_val, expect_errors=True)
            assert_equals(response.status_int, 400)
            assert_equals(response.status, '400 Bad Request')
            assert_equals(response.content_type, 'text/plain')
        except Exception:
            exception = sys.exc_info()[1]
            message = exception.args[0]
            print('FAIL: ' + message + '\nrequest = ' + invalid_val)
    # Check invalid request (duplicates)
    duplicate_values = [
            '/?id=BOU&id=BOU',
            '/?id=BOU&starttime=2016-06-06&starttime=2016-06-06',
            '/?id=BOU&endtime=2017-50-50&endtime=2017-50-50',
            '/?id=BOU&elements=H,E,Z&elements=H,E,Z',
            '/?id=BOU&sampling_period=1&sampling_period=60',
            '/?id=BOU&type=variation&type=variation',
            '/?id=BOU&format=iaga2002&format=iaga2002'
    ]
    for duplicate in duplicate_values:
        try:
            response = APP.get(duplicate, expect_errors=True)
            assert_equals(response.status_int, 400)
            assert_equals(response.status, '400 Bad Request')
            assert_equals(response.content_type, 'text/plain')
        except Exception:
            exception = sys.exc_info()[1]
            message = exception.args[0]
            print('FAIL: ' + message + '\nrequest = ' + duplicate)
    # Check valid request (upper and lower case)
    valid_requests = [
            '/?id=BOU',
            '/?id=bou',
            '/?id=bou&starttime=2016-06-06',
            '/?id=bou&starttime=2016-06-06&endtime=2016-06-07',
            '/?id=bou&elements=H,E,Z,F',
            '/?id=bou&elements=h,e,z,f',
            '/?id=BOU&sampling_period=1',
            '/?id=BOU&sampling_period=60',
            '/?id=BOU&type=variation',
            '/?id=BOU&type=VARIATION',
            '/?id=BOU&format=iaga2002',
            '/?id=BOU&format=IAGA2002'
    ]
    for request in valid_requests:
        try:
            response = APP.get(request)
            assert_equals(response.status_int, 200)
            assert_equals(response.status, '200 OK')
            assert_equals(response.content_type, 'text/plain')
        except Exception:
            exception = sys.exc_info()[1]
            message = exception.args[0]
            print('FAIL: ' + message + '\nrequest = ' + request)
