from geomagio.algorithm import FilterAlgorithm as filt
import geomagio.iaga2002 as i2
from nose.tools import assert_almost_equals


def test_process():
    """
    Check one minute filter data processing versus files generated from
    original script
    """
    # load boulder Jan 16 files from /etc/ directory
    min_iaga2002_file = open('etc/filter/BOU20180901vmin.min')
    min_iaga2002_string = min_iaga2002_file.read()
    min_iaga2002_file.close()
    sec_iaga2002_file = open('etc/filter/BOU20180901vsec.sec')
    sec_iaga2002_string = sec_iaga2002_file.read()
    sec_iaga2002_file.close()
    factory = i2.IAGA2002Factory()
    mint = factory.parse_string(min_iaga2002_string)
    sec = factory.parse_string(sec_iaga2002_string)

    # process hezf (raw) channels with loaded transform
    a = filt(inchannels=('H', 'E', 'Z', 'F'),
                         outchannels=('H', 'E', 'Z', 'F'))

    filt_bou = a.process(sec)

    # unpack channels from loaded minutes data file
    u = mint.select(channel='H')[0]
    v = mint.select(channel='E')[0]
    w = mint.select(channel='Z')[0]
    f = mint.select(channel='F')[0]
    # unpack channels from filtered data
    u_filt = filt_bou.select(channel='H')[0]
    v_filt = filt_bou.select(channel='E')[0]
    w_filt = filt_bou.select(channel='Z')[0]
    f_filt = filt_bou.select(channel='F')[0]

    for r in range(mint[0].data.size):
        assert_almost_equals(u.data[r], u_filt.data[r], 1)
        assert_almost_equals(v.data[r], v_filt.data[r], 1)
        assert_almost_equals(w.data[r], w_filt.data[r], 1)
        assert_almost_equals(f.data[r], f_filt.data[r], 1)
