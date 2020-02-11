from geomagio.algorithm import SqDistAlgorithm as sq
import numpy as np
from numpy.testing import (
    assert_allclose,
    assert_almost_equal,
    assert_array_less,
    assert_equal)


def test_sqdistalgorithm_additive1():
    """SqDistAlgorithm_test.test_sqdistalgorithm_additive1()

       Uses a simple 12 point data series to compare additive inputs with
       corresponding outputs.
    """
    # configure to test zero-step predictions of 4 "season" cycles
    m = 4
    t = np.linspace(0, 2 * np.pi, m + 1)[:-1]
    hstep = 0

    # initial slope is 0; average age is infinite
    b0 = 0
    beta = 1 / np.inf

    # initial trendline is 0; average age is 12 steps
    l0 = 0
    alpha = 1 / 12.0

    # initial seasonal correction is sinusoid; average age is 12 steps
    s0 = np.sin(t)[0:4]
    gamma = 1 / 12.0 * m

    # standard deviation of unit-amplitude sinusoid
    sigma0 = [np.sqrt(0.5)]

    # predict three cycles ahead given l0 and s0, no inputs,
    # and assume PI only grows with trendline adjustments
    yobs1 = np.zeros(12) * np.nan
    yhat1, shat1, sighat1, _, _, _, _, _ = sq.additive(
        yobs1, m, alpha=alpha, beta=beta, gamma=0,
        s0=s0, l0=l0, b0=b0, sigma0=sigma0, hstep=hstep)

    assert_almost_equal(yhat1, [0, 1, 0, -1, 0, 1, 0, -1, 0, 1, 0, -1],
        err_msg='yhat1 should almost equal simple time series')
    assert_almost_equal(shat1, [0, 1, 0, -1, 0, 1, 0, -1, 0, 1, 0, -1],
        err_msg='shat1 should almost equal simple time series')
    assert_almost_equal(sighat1, [0.70710678, 0.70955777, 0.71200031,
        0.71443451, 0.71686044, 0.71927819, 0.72168784, 0.72408947, 0.72648316,
        0.72886899, 0.73124703, 0.73361737],
        err_msg='sighat1 should almost equal simple time series')

    # predict three cycles ahead given l0 and s0, no inputs,
    # and assume PI only grows with seasonal adjustments
    yobs1 = np.zeros(12) * np.nan
    yhat1, shat1, sighat1, _, _, _, _, _ = sq.additive(
        yobs1, m, alpha=0, beta=0, gamma=gamma,
        s0=s0, l0=0, b0=0, sigma0=sigma0, hstep=hstep)

    assert_almost_equal(yhat1, [0, 1, 0, -1, 0, 1, 0, -1, 0, 1, 0, -1],
        err_msg='yhat1 should almost equal simple time series, 2nd run')
    assert_almost_equal(shat1, [0, 1, 0, -1, 0, 1, 0, -1, 0, 1, 0, -1],
        err_msg='shat1 should almost equal simple time series, 2nd run')
    assert_almost_equal(sighat1, [0.70710678, 0.70710678, 0.70710678,
        0.70710678, 0.74535599, 0.74535599, 0.74535599, 0.74535599, 0.78173596,
        0.78173596, 0.78173596, 0.78173596],
        err_msg='sighat1 should almost equal simple time series, 2nd run')

    # smooth three cycles' worth of zero-value input observations,
    # assuming only the trendline varies
    yobs1 = np.zeros(12)
    yhat1, shat1, sighat1, _, _, _, _, _ = sq.additive(
        yobs1, m, alpha=alpha, beta=0, gamma=0,
        s0=s0, l0=0, b0=0, sigma0=sigma0, hstep=hstep)

    # check output
    assert_almost_equal(yhat1, [0, 1, -0.08333333, -1.07638889, 0.01331019,
        1.01220100, -0.07214908, -1.06613666, 0.02270806, 1.02081573,
        -0.06425225, -1.0588979], 8,
        err_msg='yhat1 should almost equal simple time series, 3rd run')
    assert_almost_equal(shat1, [0, 1, 0, -1, 0, 1, 0, -1, 0, 1, 0, -1], 8,
        err_msg='shat1 should almost equal simple time series, 3rd run')
    assert_almost_equal(sighat1, [0.64818122, 0.67749945, 0.62798561,
        0.66535255, 0.61101568, 0.64444779, 0.59675623, 0.63587127, 0.58477433,
        0.62111112, 0.57470621, 0.61505552], 8,
        err_msg='sighat1 should almost equal simple time series, 3rd run')

    # smooth three cycles' worth of zero-value input observations,
    # assuming only the seasonal adjustments vary
    yobs1 = np.zeros(12)
    yhat1, shat1, sighat1, _, _, _, _, _ = sq.additive(
        yobs1, m, alpha=0, beta=0, gamma=gamma,
        s0=s0, l0=0, b0=0, sigma0=sigma0, hstep=hstep)

    # check output
    assert_almost_equal(yhat1, [0, 1, 0, -1, 0, 0.66666667, 0, -0.66666667,
        0, 0.44444444, 0, -0.44444444], 8,
        err_msg='yhat1 should almost equal simple time series, 4th run')
    assert_almost_equal(shat1, [0, 1, 0.08333333, -0.91666667, 0, 0.66666667,
        0.05555556, -0.61111111, 0, 0.44444444, 0.03703704, -0.40740741], 8,
        err_msg='shat1 should almost equal simple time series, 4th run')
    assert_almost_equal(sighat1, [0.70710678, 0.70710678, 0.70710678,
        0.70710678, 0.70710678, 0.70710678, 0.70710678, 0.70710678, 0.70710678,
        0.70710678, 0.70710678, 0.70710678], 8,
        err_msg='sighat1 should almost equal simple time series, 4th run')

    # smooth three cycles' worth of sinusoid input observations,
    # assuming only the seasonal adjustments vary, starting at zero
    yobs1 = np.concatenate((s0, s0, s0))
    yhat1, shat1, sighat1, _, _, _, _, _ = sq.additive(
        yobs1, m, alpha=0, beta=0, gamma=gamma,
        s0=s0 * 0, l0=0, b0=0, sigma0=sigma0, hstep=hstep)

    # check output
    assert_almost_equal(yhat1, [0, 0, 0, 0, 0, 0.33333333, 0, -0.33333333,
        0, 0.55555556, 0, -0.55555556], 8,
        err_msg='yhat1 should almost equal simple time series, 5th run')
    assert_almost_equal(shat1, [0, 0, -0.08333333, -0.08333333, 0, 0.33333333,
        -0.05555556, -0.38888889, 0, 0.55555555, -0.03703704, -0.59259259], 8,
        err_msg='shat1 should almost equal simple time series, 5th run')
    assert_almost_equal(sighat1, [0.70710678, 0.70710678, 0.70710678,
        0.70710678, 0.70710678, 0.70710678, 0.70710678, 0.70710678, 0.70710678,
        0.70710678, 0.70710678, 0.70710678], 8,
        err_msg='sighat1 should almost equal simple time series, 5th run')


def test_sqdistalgorithm_additive2():
    """SqDistAlgorithm_test.test_sqdistalgorithm_additive2()

       Uses synthetic data time series over 300 days to test additive method
       outputs.
    """
    # set up smoothing parameters
    m = 100                            # length of "day"
    alpha = 1.0 / 100.0 / 3.0          # average age of level is 3 "days"
    beta = 0                           # slope doesn't change
    gamma = 1.0 / 100.0 * 100.0 / 3.0  # average age of "seasonal" correction
    phi = 1                            # don't dampen the slope

    # initialize states for smoother
    l0 = None     # this uses the default initial level
    b0 = 0        # this is NOT the default initial slope
    s0 = None     # this uses default initial "seasonal" correction
    sigma0 = [0]  # this is NOT the default initial standard deviation

    # create first 50 "days" at 100 samples per synthetic "day", 0-50
    t000to050 = np.arange(5001)
    syn000to050 = 10.0 * np.sin(t000to050 * (2 * np.pi) / 100.0)

    # these are the old "defaults" computed when l0, b0, and s0 were None
    l0 = np.nanmean(syn000to050[0:1440])
    b0 = (np.nanmean(syn000to050[m:2 * m]) - np.nanmean(syn000to050[0:m])) / m
    s0 = [syn000to050[i] - l0 for i in range(m)]

    # run additive method on first 50 "days"
    (synHat000to050, sHat000to050, sigma000to050,
        syn050, s050, l050, b050, sigma050) = sq.additive(
        syn000to050, m, alpha, beta, gamma, phi,
        yhat0=None, s0=s0, l0=l0, b0=b0, sigma0=sigma0)

    # The output should track the input exactly on this simple series
    assert_equal(synHat000to050.all(), syn000to050.all(),
        'Output of additive should match simple sinusoid exactly')

    # Check max, min and average
    assert_almost_equal(np.amax(synHat000to050), 10, 8,
        'Additive output should have a max of 10.0')
    assert_almost_equal(np.amin(synHat000to050), -10, 8,
        'Additive output should have a min of -10.0')
    assert_almost_equal(np.mean(synHat000to050), 0, 8,
        'Additive output should have average of 0')

    # create 2nd set of 50 "days", 50-100
    t050to100 = np.arange(5001, 10001)
    syn050to100 = 20 + 10.0 * np.sin(t050to100 * (2 * np.pi) / 100.0)

    # run additive method on next 50 "days"
    (synHat050to100, sHat050to100, sigma050to100,
        syn100, s100, l100, b100, sigma100) = sq.additive(
        syn050to100, m, alpha, beta, gamma, phi,
        yhat0=syn050, s0=s050, l0=l050, b0=b050, sigma0=sigma050)

    # Check max, min and average
    assert_almost_equal(np.amax(synHat050to100), 30, 6,
        'Additive output should have a max of 30.0')
    assert_almost_equal(np.amin(synHat050to100), -8.81753802428088, 8,
        'Additive output should have a min of -8.81753...')
    assert_almost_equal(np.mean(synHat050to100), 19.17899833054862, 8,
        'Additive output should have average of 19.17899...')

    # the initial part of the computed series is catching up to the synthetic
    assert_array_less(synHat050to100[:555], syn050to100[:555],
        'Output of additive should begin below synthetic data')
    # short section where the series' swap places
    assert_array_less(syn050to100[555:576], synHat050to100[555:576])
    # they swap back
    assert_array_less(synHat050to100[576:655], syn050to100[576:655])
    # swap again
    assert_array_less(syn050to100[655:689], synHat050to100[655:689])
    # after the initial lag and swaps, the series' get closer and closer
    assert_allclose(syn050to100[475:], synHat050to100[475:], rtol=1e-1,
        err_msg='Additive output should trend toward synthetic data, 1e-1')
    assert_allclose(syn050to100[955:], synHat050to100[955:], rtol=1e-2,
        err_msg='Additive output should trend toward synthetic data, 1e-2')
    assert_allclose(syn050to100[1500:], synHat050to100[1500:], rtol=1e-3,
        err_msg='Additive output should trend toward synthetic data, 1e-3')
    assert_allclose(syn050to100[2100:], synHat050to100[2100:], rtol=1e-4,
        err_msg='Additive output should trend toward synthetic data, 1e-4')
    assert_allclose(syn050to100[2700:], synHat050to100[2700:], rtol=1e-5,
        err_msg='Additive output should trend toward synthetic data, 1e-5')
    assert_allclose(syn050to100[3300:], synHat050to100[3300:], rtol=1e-6,
        err_msg='Additive output should track synthetic data, 1e-6: 50-100')

    # create 3rd set of 50 "days", 100-150
    t100to150 = np.arange(10001, 15001)
    syn100to150 = 20 + 10.0 * np.sin(t100to150 * (2 * np.pi) / 100.) + \
                  20 * np.sin(t100to150 * (2 * np.pi) / 5000.0)

    # run the additive method on the 3rd set of 50 "days"
    (synHat100to150, sHat100to150, sigma100to150,
        syn150, s150, l150, b150, sigma150) = sq.additive(
        syn100to150, m, alpha, beta, gamma, phi,
        yhat0=syn100, l0=l100, b0=b100, s0=s100, sigma0=sigma100)

    # Check max, min and average
    assert_almost_equal(np.amax(synHat100to150), 49.758884882080558, 8,
        'Additive output should have a max of 49.75888...')
    assert_almost_equal(np.amin(synHat100to150), -9.7579516919427647, 8,
        'Additive output should have a min of -9.7579...')
    assert_almost_equal(np.mean(synHat100to150), 20.059589538984323, 8,
        'Additive output should have average of 20.0595...')

    # A couple of sections run pretty close together here
    assert_allclose(syn100to150[800:1900], synHat100to150[800:1900], rtol=1e-1,
        err_msg='Additive output should track synthetic data: day 100-150')

    # create 4th set of 50 "days", 150-200
    t150to200 = np.arange(15001, 20001)
    syn150to200 = 20 + (10.0 * np.sin(t150to200 * (2 * np.pi) / 100.0)) * \
                  (1 * np.cos(t150to200 * (2 * np.pi) / 5000.0))

    # run the additive method on the 4th set of 50 "days"
    (synHat150to200, sHat150to200, sigma150to200,
        syn200, s200, l200, b200, sigma200) = sq.additive(
        syn150to200, m, alpha, beta, gamma, phi,
        yhat0=syn150, l0=l150, b0=b150, s0=s150, sigma0=sigma150)

    # Check max, min and average
    assert_almost_equal(np.amax(synHat150to200), 29.573654766341747, 8,
        'Additive output should have a max of 29.5736...')
    assert_almost_equal(np.amin(synHat150to200), 7.9430807703401669, 8,
        'Additive output should have a min of 7.943...')
    assert_almost_equal(np.mean(synHat150to200), 19.911560325896119, 8,
        'Additive output should have average of 19.911...')

    # create 5th set of 50 "days", 200-250
    t200to250 = np.arange(20001, 25001)
    syn200to250 = 20 + ((10.0 * np.sin(t200to250 * (2 * np.pi) / 100.0)) *
        (1 * np.cos(t200to250 * (2 * np.pi) / 5000.0)) +
        20 * np.sin(t200to250 * (2 * np.pi) / 5000.0))

    # run the additive method on the 5th set of 50 "days"
    (synHat200to250, sHat200to250, sigma200to250,
        syn250, s250, l250, b250, sigma250) = sq.additive(
        syn200to250, m, alpha, beta, gamma, phi,
        yhat0=syn200, l0=l200, b0=b200, s0=s200, sigma0=sigma200)

    # Check max, min and average
    assert_almost_equal(np.amax(synHat200to250), 43.417782188651529, 8,
        'Additive output should have a max of 43.417...')
    assert_almost_equal(np.amin(synHat200to250), -3.4170071669726791, 8,
        'Additive output should have a min of -3.417...')
    assert_almost_equal(np.mean(synHat200to250), 20.09191068952186, 8,
        'Additive output should have average of 20.0919...')

    # create 5th set of 50 "days", 250-300
    t250to300 = np.arange(25001, 30001)
    np.random.seed(123456789)
    syn250to300 = 20 + ((10.0 * np.sin(t250to300 * (2 * np.pi) / 100.0)) *
        (1 * np.cos(t250to300 * (2 * np.pi) / 5000.0)) +
        20 * np.sin(t250to300 * (2 * np.pi) / 5000.0)) + \
        5 * np.random.randn(5000)

    # run the additive method on the 5th set of 50 "days"
    (synHat250to300, sHat250to300, sigma250to300,
        syn300, s300, l300, b300, sigma300) = sq.additive(
        syn250to300, m, alpha, beta, gamma, phi,
        yhat0=syn250, l0=l250, b0=b250, s0=s250, sigma0=sigma250)

    # Check max, min and average
    assert_almost_equal(np.amax(synHat250to300), 49.3099797861343534, 8,
        'Additive output should have a max of 49.309...')
    assert_almost_equal(np.amin(synHat250to300), -8.7531069723345301, 8,
        'Additive output should have a min of -8.783...')
    assert_almost_equal(np.mean(synHat250to300), 20.006498585824623, 8,
        'Additive output should have average of 20.006...')
