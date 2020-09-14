from numpy.testing import assert_equal
from obspy import UTCDateTime

from geomagio.api.ws.data import get_data_query
from geomagio.api.ws.DataApiQuery import OutputFormat, SamplingPeriod


def test_get_data_query():
    query = get_data_query(
        id="BOU",
        starttime="2020-09-01T00:00:01",
        endtime=None,
        elements=["X,Y,Z,F"],
        data_type="R1",
        sampling_period=60,
        format="iaga2002",
    )
    assert_equal(query.id, "BOU")
    assert_equal(query.starttime, UTCDateTime("2020-09-01T00:00:01"))
    assert_equal(query.endtime, UTCDateTime("2020-09-02T00:00:00.999"))
    assert_equal(query.elements, ["X", "Y", "Z", "F"])
    assert_equal(query.sampling_period, SamplingPeriod.MINUTE)
    assert_equal(query.format, OutputFormat.IAGA2002)
    assert_equal(query.data_type, "R1")
