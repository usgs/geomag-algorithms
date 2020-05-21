from geomagio.algorithm import DbDtAlgorithm
import geomagio.iaga2002 as i2
from numpy.testing import assert_almost_equal, assert_equal


def test_process():
    """algorithm_test.DbDtAlgorithm.test_process()

    Check DbDt result versus files generated from
    original script
    """
    # initialize DbDt object
    dbdt = DbDtAlgorithm(inchannels=["H"], outchannels=["H_DDT"], period=60)

    # load boulder May 20 files from /etc/ directory
    hez_iaga2002_file = open("etc/dbdt/BOU202005vmin.min")
    hez_iaga2002_string = hez_iaga2002_file.read()
    hez_dbdt_iaga2002_file = open("etc/dbdt/BOU202005dbdt.min")
    hez_dbdt_iaga2002_string = hez_dbdt_iaga2002_file.read()
    factory = i2.IAGA2002Factory()
    hez = factory.parse_string(hez_iaga2002_string)
    hez_dbdt = factory.parse_string(hez_dbdt_iaga2002_string)

    # process hez (raw) channels with dbdt algorithm
    result = dbdt.process(hez)

    # unpack channels from result
    rh = result.select(channel="H_DDT")[0]
    # unpack channels from BOU202005dbdt.min
    h = hez_dbdt.select(channel="H")[0]

    assert_almost_equal(h.data, rh.data, 2)
