from geomagio.algorithm import FilterAlgorithm as filt
import geomagio.iaga2002 as i2
from nose.tools import assert_equals
from nose.tools import assert_almost_equals

def test_process():
    """
    Check one minute filter data processing versus files generated from
    original script
    """


    # load boulder Jan 16 files from /etc/ directory
    min_iaga2002_file = open('etc/filter/BOU20180901vmin.min')
    min_iaga2002_string = min_iaga2002_file.read()
    sec_iaga2002_file = open('etc/filter/BOU20180901vsec.sec')
    sec_iaga2002_string = sec_iaga2002_file.read()
    factory = i2.IAGA2002Factory()
    min = factory.parse_string(min_iaga2002_string)
    sec = factory.parse_string(sec_iaga2002_string)

    # process hezf (raw) channels with loaded transform
    a = filt(inchannels=('SVH','SVE','SVZ','SSF'),
                         outchannels=('MVH','MVE','MVZ','MSF'))

    filt_bou = a.process(sec)

    # unpack channels from loaded adjusted data file
    u = min.select(channel='MVH')[0]
    v = min.select(channel='MVE')[0]
    w = min.select(channel='MVZ')[0]
    f = min.select(channel='MSF')[0]
    # unpack channels from adjusted processing of raw data
    u_filt = filt_bou.select(channel='MVH')[0]
    v_filt = filt_bou.select(channel='MVE')[0]
    w_filt = filt_bou.select(channel='MVZ')[0]
    f_filt = filt_bou.select(channel='MSF')[0]

    for r in range(min[0].data.size):
        assert_almost_equals(u.data[r], u_filt.data[r], 2)
        assert_almost_equals(v.data[r], v_filt.data[r], 2)
        assert_almost_equals(w.data[r], w_filt.data[r], 2)
        assert_almost_equals(f.data[r], f_filt.data[r], 2)
