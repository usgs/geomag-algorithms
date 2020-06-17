from numpy.testing import assert_almost_equal, assert_equal
import numpy as np
from obspy import read, UTCDateTime

from geomagio.algorithm import FilterAlgorithm
import geomagio.iaga2002 as i2


def test_second():
    """algorithm_test.FilterAlgorithm_test.test_second()
    Tests algorithm for 10Hz to second.
    """
    f = FilterAlgorithm(input_sample_period=0.1, output_sample_period=1)

    # generation of 10HZ_filter_sec.mseed
    # starttime = UTCDateTime('2020-01-06T00:00:00Z')
    # endtime = UTCDateTime('2020-01-06T04:00:00Z')
    # m = MiniSeedFactory(port=2061, host='...',
    #       convert_channels=['U', 'V', 'W'],
    #       bin_conv=500, volt_conv=100)
    # f = FilterAlgorithm(input_sample_period=0.1,
    #       output_sample_period=1.0)
    # starttime, endtime = f.get_input_interval(starttime,endtime)
    # LLO_raw = m.get_timeseries(observatory='LLO',
    #       starttime=starttime,endtime=endtime,
    #       channels=['U_Volt', 'U_Bin', 'V_Volt',
    #                 'V_Bin', 'W_Volt', 'W_Bin'],
    #       interval='tenhertz', type='variaton')
    # LLO_raw.write('10HZ_filter_sec.mseed')

    llo = read("etc/filter/10HZ_filter_sec.mseed")
    filtered = f.process(llo)

    with open("etc/filter/LLO20200106vsec.sec", "r") as f:
        iaga = i2.StreamIAGA2002Factory(stream=f)
        LLO = iaga.get_timeseries(starttime=None, endtime=None, observatory="LLO")

    u = LLO.select(channel="U")[0]
    v = LLO.select(channel="V")[0]
    w = LLO.select(channel="W")[0]

    u_filt = filtered.select(channel="U")[0]
    v_filt = filtered.select(channel="V")[0]
    w_filt = filtered.select(channel="W")[0]

    assert_almost_equal(u_filt.data, u.data, 2)
    assert_almost_equal(v_filt.data, v.data, 2)
    assert_almost_equal(w_filt.data, w.data, 2)


def test_minute():
    """algorithm_test.FilterAlgorithm_test.test_minute()
    Tests algorithm for 10Hz to minute.
    """
    f = FilterAlgorithm(input_sample_period=0.1, output_sample_period=60.0)

    # generation of 10HZ_filter_min.mseed
    # starttime = UTCDateTime('2020-01-06T00:00:00Z')
    # endtime = UTCDateTime('2020-01-06T04:00:00Z')
    # m = MiniSeedFactory(port=2061, host='...',
    #       convert_channels=['U', 'V', 'W'])
    # f = FilterAlgorithm(input_sample_period=0.1,
    #       output_sample_period=60.0)
    # starttime, endtime = f.get_input_interval(starttime,endtime)
    # LLO = m.get_timeseries(observatory='LLO',
    #       starttime=starttime,endtime=endtime,
    #       channels=['U_Volt', 'U_Bin', 'V_Volt',
    #                 'V_Bin', 'W_Volt', 'W_Bin'],
    #       interval='tenhertz', type='variaton')
    # LLO.write('10HZ_filter_min.mseed')

    llo = read("etc/filter/10HZ_filter_min.mseed")
    filtered = f.process(llo)

    with open("etc/filter/LLO20200106vmin.min", "r") as f:
        iaga = i2.StreamIAGA2002Factory(stream=f)
        LLO = iaga.get_timeseries(starttime=None, endtime=None, observatory="LLO")

    u = LLO.select(channel="U")[0]
    v = LLO.select(channel="V")[0]
    w = LLO.select(channel="W")[0]

    u_filt = filtered.select(channel="U")[0]
    v_filt = filtered.select(channel="V")[0]
    w_filt = filtered.select(channel="W")[0]

    assert_almost_equal(u_filt.data, u.data, 2)
    assert_almost_equal(v_filt.data, v.data, 2)
    assert_almost_equal(w_filt.data, w.data, 2)


def test_hour():
    """algorithm_test.FilterAlgorithm_test.test_hour()
    Tests algorithm for 10Hz to hour.
    """
    f = FilterAlgorithm(input_sample_period=0.1, output_sample_period=3600.0)

    # generation of 10HZ_filter_hor.mseed
    # starttime = UTCDateTime('2020-01-06T00:00:00Z')
    # endtime = UTCDateTime('2020-01-06T04:00:00Z')
    # m = MiniSeedFactory(port=2061, host='...',
    #       convert_channels=['U', 'V', 'W'])
    # f = FilterAlgorithm(input_sample_period=0.1,
    #       output_sample_period=3600.0)
    # starttime, endtime = f.get_input_interval(starttime,endtime)
    # LLO = m.get_timeseries(observatory='LLO',
    #       starttime=starttime,endtime=endtime,
    #       channels=['U_Volt', 'U_Bin', 'V_Volt',
    #                 'V_Bin', 'W_Volt', 'W_Bin'],
    #       interval='tenhertz', type='variaton')
    # LLO.write('10HZ_filter_hor.mseed')

    llo = read("etc/filter/10HZ_filter_hor.mseed")
    filtered = f.process(llo)

    with open("etc/filter/LLO20200106vhor.hor", "r") as f:
        iaga = i2.StreamIAGA2002Factory(stream=f)
        LLO = iaga.get_timeseries(starttime=None, endtime=None, observatory="LLO")

    u = LLO.select(channel="U")[0]
    v = LLO.select(channel="V")[0]
    w = LLO.select(channel="W")[0]

    u_filt = filtered.select(channel="U")[0]
    v_filt = filtered.select(channel="V")[0]
    w_filt = filtered.select(channel="W")[0]

    assert_almost_equal(u_filt.data, u.data, 2)
    assert_almost_equal(v_filt.data, v.data, 2)
    assert_almost_equal(w_filt.data, w.data, 2)


def test_custom():
    """algorithm_test.FilterAlgorithm_test.test_custom()
    Tests algorithm for 10Hz to second with custom filter coefficients.
    """
    f = FilterAlgorithm(
        input_sample_period=0.1,
        output_sample_period=1.0,
        coeff_filename="etc/filter/coeffs.json",
    )

    # generation of 10HZ_filter_sec.mseed
    # starttime = UTCDateTime('2020-01-06T00:00:00Z')
    # endtime = UTCDateTime('2020-01-06T04:00:00Z')
    # m = MiniSeedFactory(port=2061, host='...',
    #       convert_channels=['U', 'V', 'W'])
    # f = FilterAlgorithm(input_sample_period=0.1,
    #       output_sample_period=1.0)
    # starttime, endtime = f.get_input_interval(starttime,endtime)
    # LLO = m.get_timeseries(observatory='LLO',
    #       starttime=starttime,endtime=endtime,
    #       channels=['U_Volt', 'U_Bin', 'V_Volt',
    #                 'V_Bin', 'W_Volt', 'W_Bin'],
    #       interval='tenhertz', type='variaton')
    # LLO.write('10HZ_filter_sec.mseed')

    llo = read("etc/filter/10HZ_filter_sec.mseed")
    filtered = f.process(llo)

    with open("etc/filter/LLO20200106_custom_vsec.sec", "r") as f:
        iaga = i2.StreamIAGA2002Factory(stream=f)
        LLO = iaga.get_timeseries(starttime=None, endtime=None, observatory="LLO")

    u = LLO.select(channel="U")[0]
    v = LLO.select(channel="V")[0]
    w = LLO.select(channel="W")[0]

    u_filt = filtered.select(channel="U")[0]
    v_filt = filtered.select(channel="V")[0]
    w_filt = filtered.select(channel="W")[0]

    assert_almost_equal(u_filt.data, u.data, 2)
    assert_almost_equal(v_filt.data, v.data, 2)
    assert_almost_equal(w_filt.data, w.data, 2)


def test_starttime_shift():
    """algorithm_test.FilterAlgorithm_test.test_starttime_shift()
    Tests algorithm for second to minute with misalligned starttime(16 seconds).
    """
    f = FilterAlgorithm(input_sample_period=1.0, output_sample_period=60.0)
    # generation of BOU20200101vsec.sec
    # starttime = UTCDateTime('2020-01-01T00:00:00Z')
    # endtime = UTCDateTime('2020-01-01T00:15:00Z')
    # bou = e.get_timeseries(observatory='BOU',interval='second',type='variation',starttime=starttime,endtime=endtime,channels=["H","E","Z","F"])
    # with open('BOU20200101vsec.sec','wb') as file:
    #     i2w.write(out=file,timeseries=bou,channels=["H","E","Z","F"])
    with open("etc/filter/BOU20200101vsec.sec", "r") as file:
        iaga = i2.StreamIAGA2002Factory(stream=file)
        bou = iaga.get_timeseries(starttime=None, endtime=None, observatory="BOU")
    # check initial assumptions
    assert_equal(bou[0].stats.starttime, UTCDateTime("2020-01-01T00:00:00Z"))
    assert_equal(bou[0].stats.endtime, UTCDateTime("2020-01-01T00:15:00Z"))
    # filter should center on minute
    filtered = f.process(bou)
    assert_equal(filtered[0].stats.starttime, UTCDateTime("2020-01-01T00:01:00Z"))
    assert_equal(filtered[0].stats.endtime, UTCDateTime("2020-01-01T00:14:00Z"))
    # remove unneeded data, and verify filter works with exactly the right data
    precise = bou.trim(
        starttime=UTCDateTime("2020-01-01T00:00:15Z"),
        endtime=UTCDateTime("2020-01-01T00:14:45Z"),
    )
    filtered = f.process(precise)
    assert_equal(filtered[0].stats.starttime, UTCDateTime("2020-01-01T00:01:00Z"))
    assert_equal(filtered[0].stats.endtime, UTCDateTime("2020-01-01T00:14:00Z"))
    # remove one extra sample (filter no longer has enough to generate first/last)
    trimmed = bou.trim(
        starttime=UTCDateTime("2020-01-01T00:00:16Z"),
        endtime=UTCDateTime("2020-01-01T00:14:44Z"),
    )
    filtered = f.process(trimmed)
    assert_equal(filtered[0].stats.starttime, UTCDateTime("2020-01-01T00:02:00Z"))
    assert_equal(filtered[0].stats.endtime, UTCDateTime("2020-01-01T00:13:00Z"))


def test_even_taps():
    """algorithm_test.FilterAlgorithm_test.test_custom()
    Tests algorithm for 10Hz to second with custom filter coefficients.
    """
    f = FilterAlgorithm(
        input_sample_period=0.1,
        output_sample_period=1.0,
        coeff_filename="etc/filter/coeffs.json",
    )
    # gather original's window length
    window = f.steps[0]["window"]
    original_length = len(window)
    # remove center coefficient from original window
    f.steps[0]["window"] = np.delete(window, original_length // 2, 0)
    # check for even taps in steps' windows, add center coefficient
    f.steps = [f._prepare_step(step) for step in f.steps]
    # gather result's window length
    result_length = len(f.steps[0]["window"])
    # verify insertion of center coefficient
    original_length == result_length
