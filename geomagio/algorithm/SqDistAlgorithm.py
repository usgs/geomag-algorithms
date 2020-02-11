"""Algorithm that produces Solar Quiet (SQ), Secular Variation (SV) and
    Magnetic Disturbance (DIST).

    Algorithm for producing SQ, SV and DIST.
    This module implements Holt-Winters exponential smoothing. It predicts
    an offset-from-zero plus a "seasonal" correction given observations
    up to time t-1. Each observation's influence on the current prediction
    decreases exponentially with time according to user-supplied runtime
    configuration parameters.

    Use of fmin_l_bfgs_b to estimate parameters inspired by Andre Queiroz:
        https://gist.github.com/andrequeiroz/5888967
"""
from __future__ import absolute_import, print_function

from .. import StreamConverter
from .Algorithm import Algorithm
from .AlgorithmException import AlgorithmException
import json
import numpy as np
from obspy.core import Stream, UTCDateTime
from scipy.optimize import fmin_l_bfgs_b


class SqDistAlgorithm(Algorithm):
    """Solar Quiet, Secular Variation, and Disturbance algorithm"""

    def __init__(self, alpha=None, beta=None, gamma=None, phi=1, m=1,
                 yhat0=None, s0=None, l0=None, b0=None, sigma0=None,
                 zthresh=6, fc=0, hstep=0, statefile=None, mag=False,
                 smooth=1):
        Algorithm.__init__(self, inchannels=None, outchannels=None)
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.phi = phi
        self.m = m
        self.zthresh = zthresh
        self.fc = fc
        self.hstep = hstep
        self.statefile = statefile
        self.mag = mag
        self.smooth = smooth
        # state variables
        self.yhat0 = yhat0
        self.s0 = s0
        self.l0 = l0
        self.b0 = b0
        self.sigma0 = sigma0
        self.last_observatory = None
        self.last_channel = None
        self.last_delta = None
        self.next_starttime = None
        self.load_state()

    def get_input_interval(self, start, end, observatory=None, channels=None):
        """Get Input Interval

        start : UTCDateTime
            start time of requested output.
        end : UTCDateTime
            end time of requested output.
        observatory : string
            observatory code.
        channels : string
            input channels.

        Returns
        -------
        input_start : UTCDateTime
            start of input required to generate requested output
        input_end : UTCDateTime
            end of input required to generate requested output.
        """
        if self.mag:
            channels = ('H')
        if observatory == self.last_observatory \
                and len(channels) == 1 \
                and channels[0] == self.last_channel \
                and start == self.next_starttime:
            # state is up to date, only need new data
            return (start, end)
        # state not up to date, need to prime
        return (start - 3 * 30 * 24 * 60 * 60, end)

    def get_next_starttime(self):
        """Return the next_starttime from the state, if it is set.
        """
        return self.next_starttime

    def clear_state(self):
        """Clear in-memory state.

        Call save_state() after this method to clear filesystem state.
        """
        self.yhat0 = None
        self.s0 = None
        self.l0 = None
        self.b0 = None
        self.sigma0 = None
        self.last_observatory = None
        self.last_channel = None
        self.last_delta = None
        self.next_starttime = None

    def load_state(self):
        """Load algorithm state from a file.

        File name is self.statefile.
        """
        if self.statefile is None:
            return
        data = None
        try:
            with open(self.statefile, 'r') as f:
                data = f.read()
                data = json.loads(data)
        except Exception:
            pass
        if data is None or data == '':
            return
        self.yhat0 = data['yhat0']
        self.s0 = data['s0']
        self.l0 = data['l0']
        self.b0 = data['b0']
        self.sigma0 = data['sigma0']
        self.last_observatory = data['last_observatory']
        self.last_channel = data['last_channel']
        self.last_delta = 'last_delta' in data and data['last_delta'] or None
        self.next_starttime = UTCDateTime(data['next_starttime'])

    def save_state(self):
        """Save algorithm state to a file.

        File name is self.statefile.
        """
        if self.statefile is None:
            return
        data = {
            'yhat0': list(self.yhat0),
            's0': list(self.s0),
            'l0': self.l0,
            'b0': self.b0,
            'sigma0': list(self.sigma0),
            'last_observatory': self.last_observatory,
            'last_channel': self.last_channel,
            'last_delta': self.last_delta,
            'next_starttime': str(self.next_starttime)
        }
        with open(self.statefile, 'w') as f:
            f.write(json.dumps(data))

    def process(self, stream):
        """Run algorithm for a stream.

        Processes each trace in the stream using process_one.

        Parameters
        ----------
        stream : obspy.core.Stream
            stream of data to process

        Returns
        -------
        out : obspy.core.Stream
            stream containing 3 traces per original trace.
        """
        out = Stream()

        if self.mag:
            # convert stream to mag
            if stream.select(channel='H').count() > 0 \
                    and stream.select(channel='E').count() > 0:
                stream = StreamConverter.get_mag_from_obs(stream)
            elif stream.select(channel='X').count() > 0 \
                    and stream.select(channel='Y').count() > 0:
                stream = StreamConverter.get_mag_from_geo(stream)
            else:
                raise AlgorithmException('Unable to convert to magnetic H')
            stream = stream.select(channel='H')

        for trace in stream.traces:
            out += self.process_one(trace)
        return out

    def process_one(self, trace):
        """Run algorithm for one trace.

        Processes data and updates state.
        NOTE: state currently assumes repeated calls to process_one are
        for sequential chunks of data.

        Parameters
        ----------
        trace : obspy.core.Trace
            chunk of data to process

        Returns
        -------
        out : obspy.core.Stream
            stream containing 3 traces using channel names based on
            trace.stats.channel:
                channel_Dist
                channel_SQ
                channel_SV
        """
        out = Stream()
        # check state
        if self.last_observatory is not None \
                or self.last_channel is not None \
                or self.last_delta is not None \
                or self.next_starttime is not None:
            # have state, verify okay to proceed
            if trace.stats.station != self.last_observatory \
                    or trace.stats.channel != self.last_channel \
                    or trace.stats.delta != self.last_delta \
                    or trace.stats.starttime != self.next_starttime:
                # state not correct
                raise AlgorithmException(
                        'Inconsistent SQDist algorithm state' +
                        ' process(%s, %s, %s, %s) <> state(%s, %s, %s, %s)' %
                                (trace.stats.station,
                                trace.stats.channel,
                                trace.stats.delta,
                                trace.stats.starttime,
                                self.last_observatory,
                                self.last_channel,
                                self.last_delta,
                                self.next_starttime))
        # process
        yhat, shat, sigmahat, yhat0, s0, l0, b0, sigma0 = self.additive(
                yobs=trace.data,
                m=self.m,
                alpha=self.alpha,
                beta=self.beta,
                gamma=self.gamma,
                phi=self.phi,
                yhat0=self.yhat0,
                s0=self.s0,
                l0=self.l0,
                b0=self.b0,
                sigma0=self.sigma0,
                zthresh=self.zthresh,
                fc=self.fc,
                hstep=self.hstep,
                smooth=self.smooth)
        # update state
        self.yhat0 = yhat0
        self.s0 = s0
        self.l0 = l0
        self.b0 = b0
        self.sigma0 = sigma0
        self.last_observatory = trace.stats.station
        self.last_channel = trace.stats.channel
        self.last_delta = trace.stats.delta
        self.next_starttime = trace.stats.starttime + \
                (trace.stats.delta * trace.stats.npts)
        self.save_state()
        # create updated traces
        channel = trace.stats.channel
        # TODO: consider trimming yhat instead of adding NaNs to raw, even if
        # dist will have fewer samples than the other traces in out stream
        raw = np.concatenate((trace.data, np.full(self.fc, np.nan)))
        yhat = np.array(yhat)
        shat = np.array(shat)
        dist = np.subtract(raw, yhat)
        sq = shat
        sv = np.subtract(yhat, shat)
        # TODO: create_trace will add to stats.endtime and adjust stats.npts
        # if the data array is longer than expected, as when self.fc is non-
        # zero; HOWEVER, if self.hstep is non-zero, both stats.starttime and
        # stats.endtime must be adjusted to accomadate the time-shift.
        out += self.create_trace(channel + '_Dist', trace.stats, dist)
        out += self.create_trace(channel + '_SQ', trace.stats, sq)
        out += self.create_trace(channel + '_SV', trace.stats, sv)
        out += self.create_trace(channel + '_Sigma', trace.stats, sigmahat)
        return out

    @classmethod
    def additive(cls, yobs, m, alpha, beta, gamma, phi=1,
                 yhat0=None, s0=None, l0=None, b0=None, sigma0=None,
                 zthresh=6, fc=0, hstep=0, smooth=1):
        """Primary function for Holt-Winters smoothing/forecasting with
          damped linear trend and additive seasonal component.

        The adaptive standard deviation (sigma), multiplied by zthresh to
        determine which observations should be smoothed or ignored, is always
        updated using the latest error if a valid observation is available.
        This way, if what seemed a spike in real-time was actually a more
        permanent baseline shift, the algorithm will adjust to the new baseline
        once sigma grows enough to accommodate the errors.

        The standard deviation also updates when no obserations are present,
        but does so according to Hyndman et al (2005) prediction intervals.
        The result is a sigma that grows over gaps, and for forecasts beyond
        yobs[-1].

        Parameters
        ----------
        yobs : array_like
            input series to be smoothed/forecast
        m : int
            number of "seasons"
        alpha : float
            the level smoothing parameter (0<=alpha<=1).
        beta : float
            the slope smoothing parameter (0<=beta<=1).
        gamma : float
            the seasonal adjustment smoothing parameter (0<=gamma<=1).
        phi : float
            the dampening factor for slope (0<=phi<=1)
            (if None, phi will be estimated; default is 1)
        yhat0 : array_like
            initial yhats for hstep>0 (len(yhat0) == hstep)
            (if None, yhat0 will be set to NaNs)
        s0 : array_like
            initial set of seasonal adjustments
            (if None, default is [yobs[i] - a[0] for i in range(m)])
        l0 : float
            initial level (i.e., l(t-hstep))
            (if None, default is mean(yobs[0:m]))
        b0 : float
            initial slope (i.e., b(t-hstep))
            (if None, default is (mean(yobs[m:2*m]) - mean(yobs[0:m]))/m )
        sigma0 : float
            initial standard-deviation estimate (len(sigma0) == hstep+1)
            (if None, default is [sqrt(var(yobs))] * (hstep+1) )
        zthresh : int
            z-score threshold to determine whether yhat is updated by
            smoothing observations, or by simulation alone; if exceeded,
            only sigma is updated to reflect latest observation
        fc : int
            the number of steps beyond the end of yobs (the available
            observations) to forecast
        hstep : int
            the number of steps ahead to predict yhat[i]
            which forces an hstep prediction at each time step
        smooth: int
            period (in samples) at which Gaussian smoother will attenuate
            signal power by half

        Returns
        -------
        yhat : array_like
            series of smoothed/forecast values (aligned with yobs(t))
        shat : array_like
            series of seasonal adjustments (aligned with yobs(t))
        sigmahat : array_like
            series of time-varying standard deviations (aligned with yobs(t))
        yhat0next : array_like
            use as yhat0 when function called again with new observations
        s0next : float
            use as s0 when function called again with new observations
        l0next : float
            use as l0 when function called again with new observations
        b0next : float
            use as b0 when function called again with new observations
        sigma0next : float
            use as sigma0 when function called again with new observations
        """

        if alpha is None:
            raise AlgorithmException('alpha is required')
        if beta is None:
            raise AlgorithmException('beta is required')
        if gamma is None:
            raise AlgorithmException('gamma is required')
        if phi is None:
            raise AlgorithmException('phi is required')

        # set some default values
        if l0 is None:
            l = np.nanmean(yobs[0:int(m)])
            if np.isnan(l):
                l = 0.
        else:
            l = l0
            if not np.isscalar(l0):
                raise AlgorithmException("l0 must be a scalar")

        if b0 is None:
            b = 0
        else:
            b = b0
            if not np.isscalar(b0):
                raise AlgorithmException("b0 must be a scalar")

        if yhat0 is None:
            yhat = [np.nan for i in range(hstep)]
        else:
            yhat = list(yhat0)
            if len(yhat) != hstep:
                raise AlgorithmException("yhat0 must have length %d" % hstep)

        if s0 is None:
            s = [0 for i in range(m)]
        else:
            s = list(s0)
            if len(s) != m:
                raise AlgorithmException("s0 must have length %d " % m)

        if sigma0 is None:
            sigma = [np.sqrt(np.nanvar(yobs))] * (hstep + 1)
        else:
            sigma = list(sigma0)
            if len(sigma) != (hstep + 1):
                raise AlgorithmException(
                    "sigma0 must have length %d" % (hstep + 1))

        # generate a vector of weights that will "smooth" seasonal
        # variations locally...the quotes are because what we really
        # do is distribute the error correction across a range of
        # seasonal corrections; we do NOT convovle this filter with
        # a signal to dampen noise, as is typical. -EJR 10/2016

        # smooth parameter should specify the required cut-off period in terms
        # of discrete samples; for now, we generate a Gaussian filter according
        # to White et al. (USGS SIR 2014-5045).
        fom = 10**(-3 / 20.)  # halve power at corner frequency
        omg = np.pi / np.float64(smooth)  # corner angular frequency
        sig = np.sqrt(-2 * np.log(fom) / omg**2) + np.finfo(float).eps  # sig>0
        ts = np.linspace(np.max((-m, -3 * np.round(sig))),
                         np.min((m, 3 * np.round(sig))),
                         np.int(np.round(
                                 np.min((2 * m, 6 * np.round(sig))) + 1
                         )))
        nts = ts.size
        weights = np.exp(-0.5 * (ts / sig)**2)
        weights = weights / np.sum(weights)

        #
        # Now begin the actual Holt-Winters algorithm
        #

        # ensure mean of seasonal adjustments is zero by setting first element
        # of r equal to mean(s)
        r = [np.nanmean(s)]

        # determine sum(c^2) and phi_(j-1) for hstep "prediction interval"
        # outside of loop; initialize variables for jstep (beyond hstep)
        # prediction intervals
        sumc2_H = 1
        phiHminus1 = 0
        for h in range(1, hstep):
            phiHminus1 = phiHminus1 + phi ** (h - 1)
            sumc2_H = sumc2_H + (alpha * (1 + phiHminus1 * beta) +
                               gamma * (1 if (h % m == 0) else 0)) ** 2
        phiJminus1 = phiHminus1
        sumc2 = sumc2_H
        jstep = hstep

        # convert to, and pre-allocate numpy arrays
        yobs = np.array(yobs)
        sigma = np.concatenate((sigma, np.zeros(yobs.size + fc)))
        yhat = np.concatenate((yhat, np.zeros(yobs.size + fc)))
        r = np.concatenate((r, np.zeros(yobs.size + fc)))
        s = np.concatenate((s, np.zeros(yobs.size + fc)))

        # smooth/simulate/forecast yobs
        for i in range(len(yobs) + fc):
            # Update/append sigma for h steps ahead of i following
            # Hyndman-et-al-2005. This will be over-written if valid
            # observations exist at step i
            if jstep == hstep:
                sigma2 = sigma[i] * sigma[i]
            sigma[i + hstep + 1] = np.sqrt(sigma2 * sumc2)

            # predict h steps ahead
            yhat[i + hstep] = l + phiHminus1 * b + s[i + hstep % m]

            # discrepancy between observation and prediction at step i
            if i < len(yobs):
                et = yobs[i] - yhat[i]
            else:
                # fc>0, so simulate beyond last input
                et = np.nan

            if (np.isnan(et) or np.abs(et) > zthresh * sigma[i]):
                # forecast (i.e., update l, b, and s assuming et==0)

                # no change in seasonal adjustments
                r[i + 1] = 0 + r[i]
                s[i + m] = s[i]

                # update l before b
                l = l + phi * b
                b = phi * b

                if np.isnan(et):
                    # when forecasting, grow sigma=sqrt(var) like a prediction
                    # interval; sumc2 and jstep will be reset with the next
                    # valid observation
                    phiJminus1 = phiJminus1 + phi ** jstep
                    jstep = jstep + 1
                    sumc2 = sumc2 + (alpha * (1 + phiJminus1 * beta) +
                            gamma * (1 if (jstep % m == 0) else 0)) ** 2

                else:
                    # still update sigma using et when et > zthresh * sigma
                    # (and is not NaN)
                    sigma[i + 1] = alpha * np.abs(et) + (1 - alpha) * sigma[i]
                    jstep = hstep
            else:
                # smooth (i.e., update l, b, and s by filtering et)

                # r will be used to enforce zero-mean seasonal correction
                r[i + 1] = gamma * (1 - alpha) * et / m + r[i]

                # #update and append to s using equation-error formulation
                # s[i + m] = s[i] + gamma * (1 - alpha) * et

                # distribute error correction across range of seasonal
                # corrections according to weights calculated above
                s[i + m] = s[i] + gamma * (1 - alpha) * et * weights[nts // 2]
                s[i + m - nts // 2:i + m] = (s[i + m - nts // 2:i + m] +
                                            gamma * (1 - alpha) * et *
                                            weights[:nts // 2])
                s[i + 1:i + nts // 2 + 1] = (s[i + 1:i + nts // 2 + 1] +
                                            gamma * (1 - alpha) * et *
                                            weights[nts // 2 + 1:])

                # update l and b using equation-error formulation
                l = l + phi * b + alpha * et
                b = phi * b + alpha * beta * et

                # update sigma with et, then reset prediction interval
                sigma[i + 1] = alpha * np.abs(et) + (1 - alpha) * sigma[i]
                sumc2 = sumc2_H
                phiJminus1 = phiHminus1
                jstep = hstep

            # endif (np.isnan(et) or np.abs(et) > zthresh * sigma[i])

            # freeze state with last input for reinitialization
            if i == (len(yobs) - 1):
                yhat0 = yhat[len(yobs):(len(yobs) + hstep)].copy()
                s0 = s[len(yobs):(len(yobs) + m)].copy() - r[i + 1]
                l0 = l + r[i + 1]
                b0 = b
                sigma0 = sigma[len(yobs):(len(yobs) + hstep + 1)].copy()

        # endfor i in range(len(yobs) + fc)

        # adjustments to enforce zero-mean seasonal corrections
        l = l + r[-1]
        s = np.array(s) - np.hstack((r, np.tile(r[-1], m - 1)))

        return (yhat[:len(yobs) + fc],
                s[:len(yobs) + fc],
                sigma[1:len(yobs) + fc + 1],
                yhat0,
                s0,
                l0,
                b0,
                sigma0)

    @classmethod
    def estimate_parameters(cls, yobs, m, alpha=None, beta=None, gamma=None,
            phi=1, yhat0=None, s0=None, l0=None, b0=None, sigma0=None,
            zthresh=6, fc=0, hstep=0,
            alpha0=0.3, beta0=0.1, gamma0=0.1):
        """Estimate alpha, beta, and gamma parameters based on observed data.

        Parameters
        ----------
        yobs : array_like
            input series to be smoothed/forecast
        m : int
            number of "seasons"
        alpha : float
            the level smoothing parameter (0<=alpha<=1).
        beta : float
            the slope smoothing parameter (0<=beta<=1).
        gamma : float
            the seasonal adjustment smoothing parameter (0<=gamma<=1).
        phi : float
            the dampening factor for slope (0<=phi<=1)
            (if None, phi will be estimated; default is 1)
        yhat0 : array_like
            initial yhats for hstep>0 (len(yhat0) == hstep)
            (if None, yhat0 will be set to NaNs)
        s0 : array_like
            initial set of seasonal adjustments
            (if None, default is [yobs[i] - a[0] for i in range(m)])
        l0 : float
            initial level (i.e., l(t-hstep))
            (if None, default is mean(yobs[0:m]))
        b0 : float
            initial slope (i.e., b(t-hstep))
            (if None, default is (mean(yobs[m:2*m]) - mean(yobs[0:m]))/m )
        sigma0 : float
            initial standard-deviation estimate (len(sigma0) == hstep+1)
            (if None, default is [sqrt(var(yobs))] * (hstep+1) )
        zthresh : float
            z-score threshold to determine whether yhat is updated by
            smoothing observations, or by simulation alone; if exceeded,
            only sigma is updated to reflect latest observation
        fc : int
            the number of steps beyond the end of yobs (the available
            observations) to forecast
        hstep : int
            the number of steps ahead to predict yhat[i]
            which forces an hstep prediction at each time step
        alpha0 : float
            initial value for alpha.
            used only when alpha is None.
        beta0 : float
            initial value for beta.
            used only when beta is None.
        gamma0 : float
            initial value for gamma.
            used only when gamma is None.

        Returns
        -------
        alpha : float
            optimized parameter alpha (if alpha was None).
        beta : float
            optimized parameter beta (if beta was None).
        gamma : float
            optimized gamma, if gamma was None.
        rmse : float
            root-mean-squared-error for data using optimized parameters.
        """
        # if alpha/beta/gamma is specified, restrict bounds to "fix" parameter.
        boundaries = [
            (alpha, alpha) if alpha is not None else (0, 1),
            (beta, beta) if beta is not None else (0, 1),
            (gamma, gamma) if gamma is not None else (0, 1)
        ]
        initial_values = np.array([
            alpha if alpha is not None else alpha0,
            beta if beta is not None else beta0,
            gamma if gamma is not None else gamma0
        ])

        def func(params, *args):
            """Function that computes root-mean-squared-error based on current
            alpha, beta, and gamma parameters; as provided by fmin_l_bfgs_b.

            Parameters
            ----------
            params: list-like
                list containing alpha, beta, and gamma parameters to test
            """
            # extract parameters to fit
            alpha, beta, gamma = params
            # call Holt-Winters with additive seasonality
            yhat, _, _, _, _, _, _, _ = cls.additive(
                    yobs, m,
                    alpha=alpha, beta=beta, gamma=gamma, l0=l0, b0=b0, s0=s0,
                    zthresh=zthresh, hstep=hstep)
            # compute root-mean-squared-error of predictions
            error = np.sqrt(np.nanmean(np.square(np.subtract(yobs, yhat))))
            return error

        parameters = fmin_l_bfgs_b(func, x0=initial_values, args=(),
                bounds=boundaries, approx_grad=True)
        alpha, beta, gamma = parameters[0]
        rmse = parameters[1]
        return (alpha, beta, gamma, rmse)

    @classmethod
    def add_arguments(cls, parser):
        """Add command line arguments to argparse parser.

        Parameters
        ----------
        parser: ArgumentParser
            command line argument parser
        """
        parser.add_argument('--sqdist-alpha',
                # default=1.0 / 1440.0 / 30,
                default=0,
                help='Smoothing parameter for secular variation',
                type=float)
        parser.add_argument('--sqdist-beta',
                default=0,
                help='Smoothing parameter for slope',
                type=float)
        parser.add_argument('--sqdist-gamma',
                # default=1.0 / 30,
                default=0,
                help='Smoothing parameter for solar quiet',
                type=float)
        parser.add_argument('--sqdist-m',
                # default=1440,
                default=1,
                help='SqDist m parameter',
                type=int)
        parser.add_argument('--sqdist-mag',
                action='store_true',
                default=False,
                help='Generate sqdist based on magnetic H component')
        parser.add_argument('--sqdist-statefile',
                default=None,
                help='File to store state between calls to algorithm')
        parser.add_argument('--sqdist-zthresh',
                default=6,
                help='Set Z-score threshold',
                type=float)
        parser.add_argument('--sqdist-smooth',
                default=1,
                help='Local SQ smoothing parameter',
                type=int)

    def configure(self, arguments):
        """Configure algorithm using comand line arguments.

        Parameters
        ----------
        arguments: Namespace
            parsed command line arguments
        """
        Algorithm.configure(self, arguments)
        self.alpha = arguments.sqdist_alpha
        self.beta = arguments.sqdist_beta
        self.gamma = arguments.sqdist_gamma
        self.m = arguments.sqdist_m
        self.mag = arguments.sqdist_mag
        self.statefile = arguments.sqdist_statefile
        self.zthresh = arguments.sqdist_zthresh
        self.smooth = arguments.sqdist_smooth
        self.load_state()
