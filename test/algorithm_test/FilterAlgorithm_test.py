from geomagio.algorithm import FilterAlgorithm
from obspy.core import read
import geomagio.iaga2002 as i2
from nose.tools import assert_almost_equals


def test_process():
    """
    Check one minute filter data processing versus files generated from
    original script
    """
    # initialize 10Hz to 1sec filter
    f = FilterAlgorithm(filtertype='default',
                        input_sample_period=0.1,
                        output_sample_period=1)
    # generation of etc/filter/10HZ_filter_sec.mseed
    # starttime = UTCDateTime('2020-01-06T00:00:00Z')
    # endtime = UTCDateTime('2020-01-07T04:00:00Z')
    # starttime, endtime = f.get_input_interval(starttime, endtime)
    # m = MiniSeedFactory(port=2061, host='...',
    # convert_channels=['U', 'V', 'W'], volt_conv=100, bin_conv=500)
    # llo_for_filter = m.get_timeseries(observatory='LLO',
    #         channels=['U_Bin', 'U_Volt', 'V_Bin',
    #                  'V_Volt', 'W_Bin', 'W_Volt'],
    #         type= 'variation',
    #         interval= 'tenhertz',
    #         starttime=starttime,
    #         endtime=endtime)
    # llo_for_filter.write('/Users/pcain/geomag-algorithms/etc/filter/10HZ_filter_sec.mseed',format='MSEED')
    llo_sec = read('etc/filter/10HZ_filter_sec.mseed')
    filtered_sec = f.process(llo_sec)

    # # generation of etc/filter/10HZ_filter_min.mseed
    # f = FilterAlgorithm(filtertype='default',
    #                     input_sample_period=0.1,
    #                     output_sample_period=60)
    # starttime = UTCDateTime('2020-01-06T00:00:00Z')
    # endtime = UTCDateTime('2020-01-07T04:00:00Z')
    # starttime, endtime = f.get_input_interval(starttime, endtime)
    # m = MiniSeedFactory(port=2061, host='...',
    # convert_channels=['U', 'V', 'W'], volt_conv=100, bin_conv=500)
    # llo_for_filter = m.get_timeseries(observatory='LLO',
    #         channels=['U_Bin', 'U_Volt', 'V_Bin',
    #                  'V_Volt', 'W_Bin', 'W_Volt'],
    #         type= 'variation',
    #         interval= 'tenhertz',
    #         starttime=starttime,
    #         endtime=endtime)
    # llo_for_filter.write('/Users/pcain/geomag-algorithms/etc/filter/10HZ_filter_min.mseed',format='MSEED')

    llo_min = read('etc/filter/10HZ_filter_min.mseed')
    f = FilterAlgorithm(filtertype='default',
                        input_sample_period=0.1,
                        output_sample_period=60)
    filtered_min = f.process(llo_min)

    # # generation of etc/filter/10HZ_filter_hor.mseed
    # f = FilterAlgorithm(filtertype='default',
    #                     input_sample_period=60,
    #                     output_sample_period=3600)
    # starttime = UTCDateTime('2020-01-06T00:00:00Z')
    # endtime = UTCDateTime('2020-01-07T04:00:00Z')
    # starttime, endtime = f.get_input_interval(starttime, endtime)
    # e = EdgeFactory()
    # bou_for_filter = e.get_timeseries(observatory='BOU',
    #         channels=['H','E','Z'],
    #         type= 'variation',
    #         interval= 'minute',
    #         starttime=starttime,
    #         endtime=endtime)
    # bou_for_filter.write('/Users/pcain/geomag-algorithms/etc/filter/10HZ_filter_hor.mseed',format='MSEED')

    llo_hor = read('etc/filter/10HZ_filter_hor.mseed')
    f = FilterAlgorithm(filtertype='default',
                        input_sample_period=60,
                        output_sample_period=3600)
    filtered_hor = f.process(llo_hor)

    # read iaga files for sec, min, and hor
    with open('etc/filter/LLO20200106vsec.sec', 'r') as f:
        iaga = i2.StreamIAGA2002Factory(stream=f)
        LLO_sec = iaga.get_timeseries(starttime=None,
                    endtime=None, observatory='LLO')

    with open('etc/filter/LLO20200106vmin.min', 'r') as f:
        iaga = i2.StreamIAGA2002Factory(stream=f)
        LLO_min = iaga.get_timeseries(starttime=None,
                    endtime=None, observatory='LLO')

    with open('etc/filter/BOU20200106vhor.hor', 'r') as f:
        iaga = i2.StreamIAGA2002Factory(stream=f)
        BOU_hor = iaga.get_timeseries(starttime=None,
                    endtime=None, observatory='BOU')

    # unpack channels from loaded sec, min, and hor data files
    u_sec = LLO_sec.select(channel='U')[0]
    v_sec = LLO_sec.select(channel='V')[0]
    w_sec = LLO_sec.select(channel='W')[0]

    u_min = LLO_min.select(channel='U')[0]
    v_min = LLO_min.select(channel='V')[0]
    w_min = LLO_min.select(channel='W')[0]

    h_hor = BOU_hor.select(channel='H')[0]
    e_hor = BOU_hor.select(channel='E')[0]
    z_hor = BOU_hor.select(channel='Z')[0]

    # unpack channels from filtered data
    u_filt_sec = filtered_sec.select(channel='U')[0]
    v_filt_sec = filtered_sec.select(channel='V')[0]
    w_filt_sec = filtered_sec.select(channel='W')[0]

    u_filt_min = filtered_min.select(channel='U')[0]
    v_filt_min = filtered_min.select(channel='V')[0]
    w_filt_min = filtered_min.select(channel='W')[0]

    h_filt_hor = filtered_hor.select(channel='H')[0]
    e_filt_hor = filtered_hor.select(channel='E')[0]
    z_filt_hor = filtered_hor.select(channel='Z')[0]

    # compare filtered output to iaga files' output
    for r in range(u_sec.data.size):
        assert_almost_equals(u_filt_sec.data[r], u_sec.data[r], 1)
        assert_almost_equals(v_filt_sec.data[r], v_sec.data[r], 1)
        assert_almost_equals(w_filt_sec.data[r], w_sec.data[r], 1)

    for r in range(u_min.data.size):
        assert_almost_equals(u_filt_min.data[r], u_min.data[r], 1)
        assert_almost_equals(v_filt_min.data[r], v_min.data[r], 1)
        assert_almost_equals(w_filt_min.data[r], w_min.data[r], 1)

    for r in range(h_hor.data.size):
        assert_almost_equals(h_filt_hor.data[r], h_hor.data[r], 1)
        assert_almost_equals(e_filt_hor.data[r], e_hor.data[r], 1)
        assert_almost_equals(z_filt_hor.data[r], z_hor.data[r], 1)

    # read iaga file for custom filter(10Hz-1s)
    with open('etc/filter/LLO20200106_custom_vsec.sec', 'r') as f:
        iaga = i2.StreamIAGA2002Factory(stream=f)
        LLO_sec_custom = iaga.get_timeseries(starttime=None,
                    endtime=None, observatory='LLO')

    f = FilterAlgorithm(filtertype='custom',
                        input_sample_period=0.1,
                        output_sample_period=1,
                        coeff_filename='etc/filter/coeffs.json')

    filtered_sec_custom = f.process(llo_sec)

    # unpack channels from loaded min, sec, and hor data files
    u_sec = LLO_sec_custom.select(channel='U')[0]
    v_sec = LLO_sec_custom.select(channel='V')[0]
    w_sec = LLO_sec_custom.select(channel='W')[0]

    # unpack channels from filtered data
    u_filt_sec = filtered_sec_custom.select(channel='U')[0]
    v_filt_sec = filtered_sec_custom.select(channel='V')[0]
    w_filt_sec = filtered_sec_custom.select(channel='W')[0]

    # compare filter output with iaga file
    for r in range(u_sec.data.size):
        assert_almost_equals(u_filt_sec.data[r], u_sec.data[r], 1)
        assert_almost_equals(v_filt_sec.data[r], v_sec.data[r], 1)
        assert_almost_equals(w_filt_sec.data[r], w_sec.data[r], 1)
