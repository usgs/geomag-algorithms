import json

from numpy.testing import assert_almost_equal, assert_equal
import numpy as np
from obspy import read, UTCDateTime
import pytest

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
    assert_equal(filtered[0].stats.starttime, UTCDateTime("2020-01-06T00:00:00Z"))
    assert_equal(filtered[0].stats.endtime, UTCDateTime("2020-01-06T04:00:00Z"))


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
    assert_equal(filtered[0].stats.starttime, UTCDateTime("2020-01-06T00:00:00Z"))
    assert_equal(filtered[0].stats.endtime, UTCDateTime("2020-01-06T04:00:00Z"))


def test_hour():
    """algorithm_test.FilterAlgorithm_test.test_hour()
    Tests algorithm for 1min to hour.
    """
    f = FilterAlgorithm(input_sample_period=60.0, output_sample_period=3600.0)

    # generation of hor_filter_min.mseed
    # starttime = UTCDateTime("2020-01-31T00:00:00Z")
    # endtime = UTCDateTime("2020-01-31T04:00:00Z")
    # e = EdgeFactory()
    # f = FilterAlgorithm(input_sample_period=60.0,
    #       output_sample_period=3600.0)
    # starttime, endtime = f.get_input_interval(starttime,endtime)
    # BOU = e.get_timeseries(observatory='BOU',
    #       starttime=starttime,endtime=endtime,
    #       channels=["H", "E", "Z", "F"],
    #       interval="minute", type='variaton')
    # LLO.write('hour_filter_min.mseed')

    bou = read("etc/filter/hor_filter_min.mseed")
    filtered = f.process(bou)

    with open("etc/filter/BOU20200831vhor.hor", "r") as f:
        iaga = i2.StreamIAGA2002Factory(stream=f)
        BOU = iaga.get_timeseries(starttime=None, endtime=None, observatory="BOU")

    h = BOU.select(channel="H")[0]
    e = BOU.select(channel="E")[0]
    z = BOU.select(channel="Z")[0]
    f = BOU.select(channel="F")[0]

    h_filt = filtered.select(channel="H")[0]
    e_filt = filtered.select(channel="E")[0]
    z_filt = filtered.select(channel="Z")[0]
    f_filt = filtered.select(channel="F")[0]

    assert_almost_equal(h_filt.data, h.data, 2)
    assert_almost_equal(e_filt.data, e.data, 2)
    assert_almost_equal(z_filt.data, z.data, 2)
    assert_almost_equal(f_filt.data, f.data, 2)
    assert_equal(filtered[0].stats.starttime, UTCDateTime("2020-08-31T00:29:30"))
    assert_equal(filtered[0].stats.endtime, UTCDateTime("2020-08-31T03:29:30"))


def test_day():
    """algorithm_test.FilterAlgorithm_test.test_hour()
    Tests algorithm for 1min to day.
    """
    f = FilterAlgorithm(input_sample_period=60.0, output_sample_period=86400.0)

    # generation of day_filter_min.mseed
    # starttime = UTCDateTime("2020-01-31T00:00:00Z")
    # endtime = UTCDateTime("2020-01-31T04:00:00Z")
    # e = EdgeFactory()
    # f = FilterAlgorithm(input_sample_period=60.0,
    #       output_sample_period=86400.0)
    # starttime, endtime = f.get_input_interval(starttime,endtime)
    # BOU = e.get_timeseries(observatory='BOU',
    #       starttime=starttime,endtime=endtime,
    #       channels=["H", "E", "Z", "F"],
    #       interval="minute", type='variaton')
    # LLO.write('day_filter_min.mseed')

    bou = read("etc/filter/day_filter_min.mseed")
    filtered = f.process(bou)

    with open("etc/filter/BOU20200831vday.day", "r") as f:
        iaga = i2.StreamIAGA2002Factory(stream=f)
        BOU = iaga.get_timeseries(starttime=None, endtime=None, observatory="BOU")

    h = BOU.select(channel="H")[0]
    e = BOU.select(channel="E")[0]
    z = BOU.select(channel="Z")[0]
    f = BOU.select(channel="F")[0]

    h_filt = filtered.select(channel="H")[0]
    e_filt = filtered.select(channel="E")[0]
    z_filt = filtered.select(channel="Z")[0]
    f_filt = filtered.select(channel="F")[0]

    assert_almost_equal(h_filt.data, h.data, 2)
    assert_almost_equal(e_filt.data, e.data, 2)
    assert_almost_equal(z_filt.data, z.data, 2)
    assert_almost_equal(f_filt.data, f.data, 2)
    assert_equal(filtered[0].stats.starttime, UTCDateTime("2020-08-27T11:59:30"))
    assert_equal(filtered[0].stats.endtime, UTCDateTime("2020-08-30T11:59:30"))


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
    assert_equal(filtered[0].stats.starttime, UTCDateTime("2020-01-06T00:00:00Z"))
    assert_equal(filtered[0].stats.endtime, UTCDateTime("2020-01-06T04:00:00Z"))


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


def test_align_trace():
    """algorithm_test.FilterAlgorithm_test.test_align_trace()
    Tests algorithm for minute to hour with expected behavior, trailing samples, and missing samples
    """
    f = FilterAlgorithm(input_sample_period=60.0, output_sample_period=3600.0)
    bou = read("etc/filter/hor_filter_min.mseed")
    # check intial assumptions
    precise = f.process(bou)
    assert_equal(precise[0].stats.starttime, UTCDateTime("2020-08-31T00:29:30"))
    assert_equal(precise[0].stats.endtime, UTCDateTime("2020-08-31T03:29:30"))
    # check for filtered product producing the correct interval with trailing samples
    trimmed = bou.copy().trim(
        starttime=UTCDateTime("2020-08-31T01:00:00"),
        endtime=UTCDateTime("2020-08-31T02:04:00"),
    )
    filtered = f.process(trimmed)
    assert_equal(filtered[0].stats.starttime, UTCDateTime("2020-08-31T01:29:30"))
    assert_equal(filtered[0].stats.endtime, UTCDateTime("2020-08-31T01:29:30"))
    # test for skipped sample when not enough data is given for first interval
    trimmed = bou.copy().trim(
        starttime=UTCDateTime("2020-08-31T01:30:00"), endtime=bou[0].stats.endtime
    )
    filtered = f.process(trimmed)
    assert_equal(filtered[0].stats.starttime, UTCDateTime("2020-08-31T02:29:30"))
    assert_equal(filtered[0].stats.endtime, UTCDateTime("2020-08-31T03:29:30"))


def test_validate_step():
    """algorithm_test.FilterAlgorithm_test.test_validate_steps()
    Validates algorithm steps 10 Hz to second with custom coefficients.
    """
    with open("etc/filter/coeffs.json", "rb") as f:
        step = json.loads(f.read())
    f = FilterAlgorithm()
    numtaps = len(step["window"])
    half = numtaps // 2
    # check initial assumption
    assert_equal(numtaps % 2, 1)
    f._validate_step(step)
    # expect step to raise a value error when window has an even length
    step = {
        "window": np.delete(step["window"], numtaps // 2, 0),
        "type": "firfilter",
    }
    assert_equal(len(step["window"]) % 2, 0)
    with pytest.raises(ValueError):
        f._validate_step(step)
