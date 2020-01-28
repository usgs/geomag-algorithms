from geomagio.algorithm import FilterAlgorithm
from obspy.core import UTCDateTime, read
from geomagio.edge import MiniSeedFactory
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
    # generation of etc/filter/10HZ_filter.mseed
    # starttime = UTCDateTime('2020-01-06T00:00:00Z')
    # endtime = UTCDateTime('2020-01-07T00:00:00Z')
    # starttime, endtime = f.get_input_interval(starttime, endtime)
    # m = MiniSeedFactory(port=2061, host='...')
    # llo_for_filter = m.get_timeseries(observatory='LLO',
    #         channels=['U_Bin', 'U_Volt', 'V_Bin', 'V_Volt', 'W_Bin', 'W_Volt'],
    #         type= 'variation',
    #         interval= 'tenhertz',
    #         starttime=starttime,
    #         endtime=endtime)
    llo_for_filter = read('etc/filter/10HZ_filter.mseed')
    filtered_sec = f.process(llo_for_filter)

    # initialize 10Hz to 1min filter
    # f = FilterAlgorithm(filtertype='default',
    #                     input_sample_period=0.1,
    #                     output_sample_period=60)
    # starttime = UTCDateTime('2020-01-06T00:00:00Z')
    # endtime = UTCDateTime('2020-01-07T00:00:00Z')
    # starttime, endtime = f.get_input_interval(starttime, endtime)
    # m = MiniSeedFactory(port=2061, host='...')
    # llo_for_filter = m.get_timeseries(observatory='LLO',
    #         channels=['U_Bin', 'U_Volt', 'V_Bin', 'V_Volt', 'W_Bin', 'W_Volt'],
    #         type='variation',
    #         interval='tenhertz',
    #         starttime=starttime,
    #         endtime=endtime)
    # filtered_minute = f.process(llo_for_filter)

    # initialize 10Hz to 1hour filter
    # f = FilterAlgorithm(filtertype='default',
    #                     input_sample_period=0.1,
    #                     output_sample_period=3600)
    # starttime = UTCDateTime('2020-01-06T00:00:00Z')
    # endtime = UTCDateTime('2020-01-07T00:00:00Z')
    # starttime, endtime = f.get_input_interval(starttime, endtime)
    # m = MiniSeedFactory(port=2061, host='...')
    # llo_for_filter = m.get_timeseries(observatory='LLO',
    #         channels=['U_Bin', 'U_Volt', 'V_Bin', 'V_Volt', 'W_Bin', 'W_Volt'],
    #         type='variation',
    #         interval='tenhertz',
    #         starttime=starttime,
    #         endtime=endtime)
    # filtered_hour = f.process(llo_for_filter)

    # read iaga files for sec, min, and hour
    sec_iaga2002_file = open('etc/filter/LLO20200107vsec.sec')
    sec_iaga2002_string = sec_iaga2002_file.read()
    sec_iaga2002_file.close()

    min_iaga2002_file = open('etc/filter/LLO20200107vmin.min')
    min_iaga2002_string = min_iaga2002_file.read()
    min_iaga2002_file.close()

    hor_iaga2002_file = open('etc/filter/LLO20200107vhor.hor')
    hor_iaga2002_string = hor_iaga2002_file.read()
    hor_iaga2002_file.close()

    factory = i2.IAGA2002Factory()
    _sec_ = factory.parse_string(sec_iaga2002_string)
    _min_ = factory.parse_string(min_iaga2002_string)
    _hor_ = factory.parse_string(hor_iaga2002_string)

    # unpack channels from loaded minutes data file
    u_sec = _sec_.select(channel='U')[0]
    v_sec = _sec_.select(channel='V')[0]
    w_sec = _sec_.select(channel='W')[0]

    u_min = _min_.select(channel='U')[0]
    v_min = _min_.select(channel='V')[0]
    w_min = _min_.select(channel='W')[0]

    u_hor = _hor_.select(channel='U')[0]
    v_hor = _hor_.select(channel='V')[0]
    w_hor = _hor_.select(channel='W')[0]

    # unpack channels from filtered data
    u_filt_sec = filtered_sec.select(channel='U')[0]
    v_filt_sec = filtered_sec.select(channel='V')[0]
    w_filt_sec = filtered_sec.select(channel='W')[0]

    # u_filt_min = filtered_minute.select(channel='U')[0]
    # v_filt_min = filtered_minute.select(channel='V')[0]
    # w_filt_min = filtered_minute.select(channel='W')[0]

    # u_filt_hor = filtered_hour.select(channel='U')[0]
    # v_filt_hor = filtered_hour.select(channel='V')[0]
    # w_filt_hor = filtered_hour.select(channel='W')[0]

    # compare filtered output to iaga files' output
    for r in range(u_sec.data.size):
        assert_almost_equals(u_filt_sec.data[r], u_sec.data[r], 1)
        assert_almost_equals(v_filt_sec.data[r], v_sec.data[r], 1)
        assert_almost_equals(w_filt_sec.data[r], w_sec.data[r], 1)

    # for r in range(u_min.data.size):
    #     assert_almost_equals(u_filt_min.data[r], u_min.data[r], 1)
    #     assert_almost_equals(v_filt_min.data[r], v_min.data[r], 1)
    #     assert_almost_equals(w_filt_min.data[r], w_min.data[r], 1)

    # for r in range(u_hor.data.size):
    #     assert_almost_equals(u_filt_hor.data[r], u_hor.data[r], 1)
    #     assert_almost_equals(v_filt_hor.data[r], v_hor.data[r], 1)
    #     assert_almost_equals(w_filt_hor.data[r], w_hor.data[r], 1)

    # initialize custom filter
    # f = FilterAlgorithm(filtertype='custom',
    #                     coeff_filename='etc/filter/coeffs.json',
    #                     input_sample_period=0.1,
    #                     output_sample_period=1)
    # starttime = UTCDateTime('2020-01-06T00:00:00Z')
    # endtime = UTCDateTime('2020-01-07T00:00:00Z')
    # starttime, endtime = f.get_input_interval(starttime, endtime)
    # m = MiniSeedFactory(port=2061, host='...')
    # llo_for_filter = m.get_timeseries(observatory='LLO',
    #         channels=['U_Bin', 'U_Volt', 'V_Bin', 'V_Volt', 'W_Bin', 'W_Volt'],
    #         type='variation',
    #         interval='tenhertz',
    #         starttime=starttime,
    #         endtime=endtime)
    # filtered_hour = f.process(llo_for_filter)

    # unpack channels from filtered data
    # u_filt_sec = filtered_sec.select(channel='U')[0]
    # v_filt_sec = filtered_sec.select(channel='V')[0]
    # w_filt_sec = filtered_sec.select(channel='W')[0]

    # # compare filter output with iaga file
    # for r in range(u_sec.data.size):
    #     assert_almost_equals(u_filt_sec.data[r], u_sec.data[r], 1)
    #     assert_almost_equals(v_filt_sec.data[r], v_sec.data[r], 1)
    #     assert_almost_equals(w_filt_sec.data[r], w_sec.data[r], 1)
