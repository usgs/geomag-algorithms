"""Tests for RawInputClient.py"""

import numpy
from datetime import datetime
import logging
from obspy.core import Stats, Trace, UTCDateTime
from geomagio.edge import EdgeFactory, RawInputClient
from numpy.testing import assert_equal


class MockRawInputClient(RawInputClient):
    def __init__(self, **kwargs):
        RawInputClient.__init__(self, **kwargs)
        self.last_send = []

    def _send(self, buf):
        """stub out send method to capture data that would be sent."""
        self.last_send.append(buf)


def test_raw_input_client():
    """edge_test.RawInputClient_test.test_raw_input_client()"""
    network = "NT"
    station = "BOU"
    channel = "MVH"
    location = "R0"
    data = [0, 1, 2, 3, 4, 5]
    starttime = UTCDateTime("2019-12-01")

    trace = Trace(
        numpy.array(data, dtype=numpy.float64),
        Stats(
            {
                "channel": channel,
                "delta": 60.0,
                "location": location,
                "network": network,
                "npts": len(data),
                "starttime": starttime,
                "station": station,
            }
        ),
    )

    client = MockRawInputClient(
        tag="tag",
        host="host",
        port="port",
        station=station,
        channel=channel,
        location=location,
        network=network,
    )
    trace_send = EdgeFactory()._convert_trace_to_int(trace.copy())
    client.send_trace("minute", trace_send)
    # verify data was sent
    assert_equal(len(client.last_send), 1)


def test__get_tag():
    """edge_test.RawInputClient_test.test__get_tag()"""
    network = "NT"
    station = "BOU"
    channel = "MVH"
    location = "R0"
    client = MockRawInputClient(
        tag="tag",
        host="host",
        port="port",
        station=station,
        channel=channel,
        location=location,
        network=network,
    )
    tag_send = client._get_tag()
    assert_equal(tag_send is not None, True)


def test__get_time_values(caplog):
    """edge_test.RawInputClient_test.test__get_time_values()"""
    network = "NT"
    station = "BOU"
    channel = "MVH"
    location = "R0"
    client = MockRawInputClient(
        tag="tag",
        host="host",
        port="port",
        station=station,
        channel=channel,
        location=location,
        network=network,
    )

    # test rounding up of microsecond value
    time = UTCDateTime("2020-10-07T00:00:15.196855Z")
    yr, doy, secs, usecs = client._get_time_values(time)
    assert_equal(yr, 2020)
    assert_equal(doy, 281)
    assert_equal(secs, 15)
    assert_equal(usecs, 197000)
    # test rounding down of microsecond value
    time = UTCDateTime("2020-10-07T00:00:15.196455Z")
    yr, doy, secs, usecs = client._get_time_values(time)
    assert_equal(yr, 2020)
    assert_equal(doy, 281)
    assert_equal(secs, 15)
    assert_equal(usecs, 196000)
    # test top of second adjustment
    time = UTCDateTime("2020-10-07T00:00:00.999999Z")
    yr, doy, secs, usecs = client._get_time_values(time)
    assert_equal(yr, 2020)
    assert_equal(doy, 281)
    assert_equal(secs, 1)
    assert_equal(usecs, 0)
    # test top of day adjustment
    time = UTCDateTime("2020-10-07T23:59:59.999999Z")
    yr, doy, secs, usecs = client._get_time_values(time)
    assert_equal(yr, 2020)
    assert_equal(doy, 282)
    assert_equal(secs, 0)
    assert_equal(usecs, 0)
    # assert if previous 4 tests generate 4 warning messages
    assert_equal(len(caplog.messages), 4)

    # clear warnings from log
    caplog.clear()
    # test ideal case
    time = UTCDateTime("2020-10-07T00:00:00.232000Z")
    yr, doy, secs, usecs = client._get_time_values(time)
    assert_equal(yr, 2020)
    assert_equal(doy, 281)
    assert_equal(secs, 0)
    assert_equal(usecs, 232000)
    # assert if previous test does not generate a warning message
    assert_equal(len(caplog.messages), 0)
