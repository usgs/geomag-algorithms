from geomagio.algorithm import AdjustedAlgorithm as adj
import geomagio.iaga2002 as i2
from nose.tools import assert_equals
from nose.tools import assert_almost_equals


def test_construct():
    """
    path to
    """
    matrix = None
    pier_correction = None
    a = adj(matrix, pier_correction, 'etc/adjusted/adjbou_state_.json')

    assert_almost_equals(a.matrix[0, 0], 9.83427577e-01, 6)

    assert_equals(a.pier_correction, -22)


def test_process():
    """
    Check adjusted data processing versus files generated from
    original script
    """
    matrix = None
    pier_correction = None
    a = adj(matrix, pier_correction, 'etc/adjusted/adjbou_state_.json')

    hezf_iaga2002_file = open('etc/adjusted/BOU201601vmin.min')
    hezf_iaga2002_string = hezf_iaga2002_file.read()
    xyzf_iaga2002_file = open('etc/adjusted/BOU201601adj.min')
    xyzf_iaga2002_string = xyzf_iaga2002_file.read()
    factory = i2.IAGA2002Factory()
    hezf = factory.parse_string(hezf_iaga2002_string)
    xyzf = factory.parse_string(xyzf_iaga2002_string)

    adj_bou = a.process(hezf)
    x = xyzf.select(channel='X')[0]
    y = xyzf.select(channel='Y')[0]
    z = xyzf.select(channel='Z')[0]
    f = xyzf.select(channel='F')[0]
    x_adj = adj_bou.select(channel='X')[0]
    y_adj = adj_bou.select(channel='Y')[0]
    z_adj = adj_bou.select(channel='Z')[0]
    f_adj = adj_bou.select(channel='F')[0]

    for r in range(hezf[0].data.size):
        assert_almost_equals(x.data[r], x_adj.data[r], 1)
        assert_almost_equals(y.data[r], y_adj.data[r], 1)
        assert_almost_equals(z.data[r], z_adj.data[r], 1)
        assert_almost_equals(f.data[r], f_adj.data[r], 1)
