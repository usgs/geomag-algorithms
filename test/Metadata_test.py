from obspy import UTCDateTime
from geomagio.Metadata import get_instrument
from numpy.testing import assert_equal


METADATA1 = {
    "station": "TST",
    "start_time": None,
    "end_time": UTCDateTime("2020-02-02T00:00:00Z"),
}

METADATA2 = {
    "station": "TST",
    "start_time": UTCDateTime("2020-02-02T00:00:00Z"),
    "end_time": UTCDateTime("2020-02-03T00:00:00Z"),
}

METADATA3 = {
    "station": "TST",
    "start_time": UTCDateTime("2020-02-03T00:00:00Z"),
    "end_time": None,
}

TEST_METADATA = [METADATA1, METADATA2, METADATA3]


def test_get_instrument_after():
    """Request an interval after the last entry, that has start_time None"""
    matches = get_instrument(
        "TST",
        UTCDateTime("2021-02-02T00:00:00Z"),
        UTCDateTime("2022-01-02T00:00:00Z"),
        TEST_METADATA,
    )
    assert_equal(matches, [METADATA3])


def test_get_instrument_before():
    """Request an interval before the first entry, that has start_time None"""
    matches = get_instrument(
        "TST",
        UTCDateTime("2019-02-02T00:00:00Z"),
        UTCDateTime("2020-01-02T00:00:00Z"),
        TEST_METADATA,
    )
    assert_equal(matches, [METADATA1])


def test_get_instrument_inside():
    """Request an interval that is wholly contained by one entry"""
    matches = get_instrument(
        "TST",
        UTCDateTime("2020-02-02T01:00:00Z"),
        UTCDateTime("2020-02-02T02:00:00Z"),
        TEST_METADATA,
    )
    assert_equal(matches, [METADATA2])


def test_get_instrument_span():
    """Request a time interval that spans multiple entries"""
    matches = get_instrument(
        "TST",
        UTCDateTime("2020-01-02T00:00:00Z"),
        UTCDateTime("2020-02-02T01:00:00Z"),
        TEST_METADATA,
    )
    assert_equal(matches, [METADATA1, METADATA2])


def test_get_instrument_unknown():
    """Request an unknown observatory"""
    matches = get_instrument(
        "OTHER",
        UTCDateTime("2020-01-02T00:00:00Z"),
        UTCDateTime("2020-02-02T01:00:00Z"),
        TEST_METADATA,
    )
    assert_equal(matches, [])
