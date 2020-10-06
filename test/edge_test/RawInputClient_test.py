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
    # define expected date from _get_time_values
    expected_time = UTCDateTime(2020, 10, 7, 0, 0, 0, 0)
    # define date with residual microseconds
    residual_time = UTCDateTime(2020, 10, 6, 23, 59, 59, 999999)
    r_yr, r_doy, r_secs, r_usecs = client._get_time_values(residual_time)
    # check if input microsecond value changes within function
    message = caplog.messages[0]
    assert_equal(
        message,
        "residual microsecond values encountered, rounding to nearest microsecond",
    )
    e_yr, e_doy, e_secs, e_usecs = client._get_time_values(expected_time)
    # test if residual result matches expected result
    assert_equal(e_yr, r_yr)
    assert_equal(e_doy, r_doy)
    assert_equal(e_secs, r_secs)
    assert_equal(e_usecs, r_usecs)
