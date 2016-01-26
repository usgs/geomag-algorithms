#! /usr/bin/env python
from geomagio.algorithm import SQDistAlgorithm
from nose.tools import assert_equals
import numpy as np


def test_sqdistalgorithm_additive():
    """SqDistAlgorithm_test.test_sqdistalgorithm_additive()

    """
    # set up smoothing parameters
    m = 100                        # length of "day"
    alpha = 1. / 100. / 3.         # average age of level is 3 "days"
    beta = 0                       # slope doesn't change
    gamma = 1. / 100. * 100. / 3.  # average age of "seasonal" correction
    phi = 1                        # don't dampen the slope

    # initialize states for smoother
    l0 = None     # this uses the default initial level
    b0 = 0        # this is NOT the default initial slope
    s0 = None     # this uses default initial "seasonal" correction
    sigma0 = [0]  # this is NOT the default initial standard deviation

    # create first 50 "days" at 100 samples per synthetic "day"
    t000to050 = np.arange(5001)
    syn000to050 = 10. * np.sin(t000to050 * (2 * np.pi) / 100.)

    # run additive method on first 50 "days"
    (synHat000to050, sHat000to050, sigma000to050,
    syn050, s050, l050, b050, sigma050) = SQDistAlgorithm.additive(
                                syn000to050, m,
                                alpha, beta, gamma, phi,
                                yhat0=None, l0=l0, b0=b0, s0=s0, sigma0=sigma0)

    assert_equals(synHat000to050, syn000to050)

    # create next 50 "days"
    t050to100 = np.arange(5001,10001)
    syn050to100 = 20 + 10. * np.sin(t050to100 * (2*np.pi)/100.)

    # run additive method on next 50 "days"
    (synHat050to100, sHat050to100, sigma050to100,
     syn100, s100, l100, b100, sigma100) = SQDistAlgorithm.additive(
                                syn050to100, m,
                                alpha, beta, gamma, phi,
                                yhat0=syn050, l0=l050, b0=b050, s0=s050,
                                sigma0=sigma050)

    plt.figure(figsize=(16,4))
    plt.plot(t050to100/100., syn050to100, color='blue')
    plt.plot(t050to100/100., synHat050to100, color='green')
    plt.plot(t050to100/100., synHat050to100 - sHat050to100, color='red')
