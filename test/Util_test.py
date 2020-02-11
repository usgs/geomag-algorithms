#! /usr/bin/env python
import os.path
import shutil
from numpy.testing import assert_equal
from geomagio import Util
from obspy.core import UTCDateTime


def test_get_file_for_url__throws_exception():
    """Util_test.test_get_file_for_url__throws_exception()
    """
    # throws exception for non "file://" urls
    try:
        Util.get_file_from_url('http://someserver/path')
        assert False, ('expected exception')
    except Exception:
        pass


def test_get_file_for_url__parses_file_urls():
    """Util_test.test_get_file_for_url__parses_file_urls()
    """
    # parses file urls
    f = Util.get_file_from_url('file://./somefile')
    assert_equal(f, './somefile')


def test_get_file_for_url__creates_directories():
    """Util_test.test_get_file_for_url__creates_directories()
    """
    # creates directories if requested
    if os.path.isdir('/tmp/_geomag_algorithms_test_'):
        shutil.rmtree('/tmp/_geomag_algorithms_test_')
    f = Util.get_file_from_url('file:///tmp/_geomag_algorithms_test_/somefile',
            createParentDirectory=True)
    if not os.path.isdir('/tmp/_geomag_algorithms_test_'):
        assert False, ('directory not created')
    shutil.rmtree('/tmp/_geomag_algorithms_test_')
    assert_equal(f, '/tmp/_geomag_algorithms_test_/somefile')


def test_get_interval__defaults():
    """Util_test.test_get_interval()
    """
    starttime = UTCDateTime('2015-01-01T00:00:00Z')
    endtime = UTCDateTime('2015-02-01T00:00:00Z')
    intervals = Util.get_intervals(starttime, endtime)
    assert_equal(len(intervals), 31)


def test_get_interval__custom_size():
    """Util_test.test_get_interval__custom_size()
    """
    starttime = UTCDateTime('2015-01-01T00:00:00Z')
    endtime = UTCDateTime('2015-01-02T00:00:00Z')
    intervals = Util.get_intervals(starttime, endtime, size=3600)
    assert_equal(len(intervals), 24)


def test_get_interval__negative_size():
    """Util_test.test_get_interval__negative_size()
    """
    starttime = UTCDateTime('2015-01-01T00:00:00Z')
    endtime = UTCDateTime('2015-01-02T00:00:00Z')
    intervals = Util.get_intervals(starttime, endtime, size=-1)
    assert_equal(len(intervals), 1)
    assert_equal(intervals[0]['start'], starttime)
    assert_equal(intervals[0]['end'], endtime)


def test_get_interval__trim():
    """Util_test.test_get_interval__trim()
    """
    starttime = UTCDateTime('2015-01-01T01:00:00Z')
    endtime = UTCDateTime('2015-01-02T00:00:00Z')
    intervals = Util.get_intervals(starttime, endtime, trim=True)
    assert_equal(intervals[0]['start'], starttime)
