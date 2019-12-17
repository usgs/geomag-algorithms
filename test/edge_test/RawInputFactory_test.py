"""Tests for RawInputFactory.py"""

import numpy
from obspy.core import Stats, Trace, UTCDateTime
from geomagio.edge import EdgeFactory, RawInputClient
from nose.tools import assert_equals


class TestRawInputClient(RawInputClient):
    def __init__(self, **kwargs):
        RawInputClient.__init__(self, **kwargs)
        self.last_send = []

    def _send(self, buf):
        """stub out send method to capture data that would be sent."""
        self.last_send.append(buf)


def test_raw_input_client():
    """edge_test.RawInputClient_test.test_raw_input_client()
    """
    network = 'NT'
    station = 'BOU'
    channel = 'MVH'
    location = 'R0'
    data = [0, 1, 2, 3, 4, 5]
    starttime = UTCDateTime('2019-12-01')

    trace = Trace(
            numpy.array(data, dtype=numpy.float64),
            Stats({
                'channel': channel,
                'delta': 60.0,
                'location': location,
                'network': network,
                'npts': len(data),
                'starttime': starttime,
                'station': station
            }))

    client = TestRawInputClient(tag='tag', host='host', port='port',
            station=station, channel=channel,
            location=location, network=network)
    trace_send = EdgeFactory()._convert_trace_to_int(trace.copy())
    client.send_trace('minute', trace_send)
    # verify data was sent
    assert_equals(len(client.last_send), 1)
