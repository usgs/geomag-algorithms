from geomagio.algorithm import AdjustedAlgorithm as adj
from geomagio.edge import EdgeFactory as edge
from nose.tools import assert_equals
from nose.tools import assert_almost_equals
from obspy.core import UTCDateTime


def test_construct():
    """
    path to
    """
    matrix = None
    pier_correction = None
    a = adj(matrix, pier_correction, 'etc/adjusted/adjbou_state_.json')

    assert_almost_equals(a.matrix[0, 0], 9.83427577e-01, 6)

    assert_equals(a.pier_correction, -22)


def test_trivial():
    """
    """

    assert_equals(3, 3)


def test_process():
    """
    """
    matrix = None
    pier_correction = None
    a = adj(matrix, pier_correction, 'etc/adjusted/adjbou_state_.json')

    factory = edge(host='137.227.224.97', port=2060)
    hezf = factory.get_timeseries(observatory='BOU',
        interval='minute',
        type='variation',
        channels=('H', 'E', 'Z', 'F'),
        starttime=UTCDateTime('2016-01-01T00:00:00Z'),
        endtime=UTCDateTime('2016-01-31T00:05:00Z'))

    adj_bou = a.process(hezf)

    assert_equals(hezf[0].data[0] == adj_bou[0].data[0], False)
