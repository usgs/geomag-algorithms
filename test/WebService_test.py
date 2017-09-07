"""Tests for WebService.py"""

from nose.tools import assert_equals
import sys
from webtest import TestApp

from geomagio.edge import EdgeFactory
from geomagio.WebService import WebService


app = TestApp(WebService(EdgeFactory()))


def test_bad_requests():
    """WebService_test.test_bad_requests()
    """
    # Check bad request (values)
    bad_values = [
        '/',
        '/?id=bad',
        '/?id=BOU&starttime=2017-50-50',
        '/?id=BOU&starttime=2016-06-06&endtime=2017-50-50',
        '/?id=BOU&starttime=2016-06-06&endtime=2016-06-05',
        '/?id=BOU&elements=H,E,D,Z,F',
        '/?id=BOU&type=bad',
        '/?id=BOU&format=bad'
    ]
    for bad_val in bad_values:
        try:
            response = app.get(bad_val, expect_errors=True)
            assert_equals(response.status_int, 400)
        except Exception:
            exception = sys.exc_info()[1]
            message = exception.args[0]
            print('FAIL: ' + message + '\nrequest = ' + bad_val)
    # Check bad request (duplicates)
    duplicate_values = [
            '/?id=BOU&id=BOU',
            '/?id=BOU&starttime=2016-06-06&starttime=2016-06-06',
            '/?id=BOU&endtime=2017-50-50&endtime=2017-50-50',
            '/?id=BOU&elements=H,E,Z&elements=H,E,Z',
            '/?id=BOU&type=variation&type=variation',
            '/?id=BOU&format=iaga2002&format=iaga2002'
    ]
    for duplicate in duplicate_values:
        try:
            response = app.get(duplicate, expect_errors=True)
            assert_equals(response.status_int, 400)
        except Exception:
            exception = sys.exc_info()[1]
            message = exception.args[0]
            print('FAIL: ' + message + '\nrequest = ' + duplicate)

def test_good_requests():
    """WebService_test.test_good_requests()
    """
    # Check for upper and lower case
    good_requests = [
            '/?id=BOU',
            '/?id=bou',
            '/?id=bou&starttime=2016-06-06',
            '/?id=bou&starttime=2016-06-06&endtime=2016-06-07',
            '/?id=bou&elements=H,E,Z,F',
            '/?id=bou&elements=h,e,z,f',
            '/?id=BOU&type=variation',
            '/?id=BOU&type=VARIATION',
            '/?id=BOU&format=iaga2002',
            '/?id=BOU&format=IAGA2002'
    ]
    for request in good_requests:
        try:
            response = app.get(request)
            assert_equals(response.status_int, 200)
        except Exception:
            exception = sys.exc_info()[1]
            message = exception.args[0]
            print('FAIL: ' + message + '\nrequest = ' + request)
