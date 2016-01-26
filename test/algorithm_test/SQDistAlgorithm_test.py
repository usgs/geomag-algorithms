from geomagio.algorithm import SqDistAlgorithm
from nose.tools import assert_equals
import numpy as np


def test_sqdistalgorithm_additive():
    """SqDistAlgorithm_test.test_sqdistalgorithm_additive()

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

    # create first 50 "days" at 100 samples per synthetic "day"
    t000to050 = np.arange(5001)
    syn000to050 = 10.0 * np.sin(t000to050 * (2 * np.pi) / 100.0)

    # run additive method on first 50 "days"
    (synHat000to050, sHat000to050, sigma000to050,
    syn050, s050, l050, b050, sigma050, alpha, beta,
                                gamma) = SqDistAlgorithm.additive(
                                syn000to050, m,
                                alpha, beta, gamma, phi,
                                yhat0=None, s0=s0, l0=l0, b0=b0, sigma0=sigma0)

    # The output should track the input exactly on this simple series
    assert_equals(synHat000to050.all(), syn000to050.all())

    # create 2nd set of 50 "days" (shifted up from 1st 50 "days")
    # t050to100 = np.arange(5001, 10001)
    # syn050to100 = 20 + 10.0 * np.sin(t050to100 * (2 * np.pi) / 100.0)

    # run additive method on next 50 "days"
    # (synHat050to100, sHat050to100, sigma050to100,
    # syn100, s100, l100, b100, sigma100) = additive(
    #                            syn050to100, m,
    #                            alpha, beta, gamma, phi,
    #                            yhat0=syn050, l0=l050, b0=b050, s0=s050,
    #                            sigma0=sigma050)

    # print(synHat050to100 - sHat050to100)

    # create 3rd set of 50 "days"
    # t100to150 = np.arange(10001, 15001)
    # syn100to150 = 20 + 10.0 * np.sin(t100to150 * (2 * np.pi) / 100.) + \
    #            20 * np.sin(t100to150 * (2 * np.pi) / 5000.0)
