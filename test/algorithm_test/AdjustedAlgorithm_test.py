from geomagio.algorithm import AdjustedAlgorithm as adj
import geomagio.iaga2002 as i2
from numpy.testing import assert_almost_equal, assert_equal


def test_construct():
    """algorithm_test.AdjustedAlgorithm_test.test_construct()
    """
    matrix = None
    pier_correction = None
    # load adjusted data transform matrix and pier correction
    a = adj(matrix, pier_correction, 'etc/adjusted/adjbou_state_.json')

    assert_almost_equal(a.matrix[0, 0], 9.83427577e-01, 6)

    assert_equal(a.pier_correction, -22)


def test_process():
    """algorithm_test.AdjustedAlgorithm_test.test_process()

    Check adjusted data processing versus files generated from
    original script
    """
    matrix = None
    pier_correction = None
    # load adjusted data transform matrix and pier correction
    a = adj(matrix, pier_correction, 'etc/adjusted/adjbou_state_.json')

    # load boulder Jan 16 files from /etc/ directory
    hezf_iaga2002_file = open('etc/adjusted/BOU201601vmin.min')
    hezf_iaga2002_string = hezf_iaga2002_file.read()
    xyzf_iaga2002_file = open('etc/adjusted/BOU201601adj.min')
    xyzf_iaga2002_string = xyzf_iaga2002_file.read()
    factory = i2.IAGA2002Factory()
    hezf = factory.parse_string(hezf_iaga2002_string)
    xyzf = factory.parse_string(xyzf_iaga2002_string)

    # process hezf (raw) channels with loaded transform
    adj_bou = a.process(hezf)

    # unpack channels from loaded adjusted data file
    x = xyzf.select(channel='X')[0]
    y = xyzf.select(channel='Y')[0]
    z = xyzf.select(channel='Z')[0]
    f = xyzf.select(channel='F')[0]
    # unpack channels from adjusted processing of raw data
    x_adj = adj_bou.select(channel='X')[0]
    y_adj = adj_bou.select(channel='Y')[0]
    z_adj = adj_bou.select(channel='Z')[0]
    f_adj = adj_bou.select(channel='F')[0]

    assert_almost_equal(x.data, x_adj.data, 2)
    assert_almost_equal(y.data, y_adj.data, 2)
    assert_almost_equal(z.data, z_adj.data, 2)
    assert_almost_equal(f.data, f_adj.data, 2)
