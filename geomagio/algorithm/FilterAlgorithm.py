from __future__ import absolute_import

from .Algorithm import Algorithm
import json
import numpy as np
from numpy.lib import stride_tricks as npls
import scipy.signal as sps
from obspy.core import Stream, Stats
import sys


class FilterAlgorithm(Algorithm):
    """
        Filter Algorithm that filters and downsamples data from one second
    """

    def __init__(self, decimation=None, window=None, interval=None,
                 location=None, inchannels=None, outchannels=None,
                 data_type=None):
        Algorithm.__init__(self, inchannels=inchannels,
            outchannels=outchannels)
        self.numtaps=91
        # get filter window (standard intermagnet one-minute filter)
        self.window = sps.get_window(window=('gaussian', 15.8734),
                                             Nx=self.numtaps)
        # normalize filter window
        self.window = self.window/np.sum(self.window)
        self.decimation = 60
        self.sample_period = 1.0
        self.data_type = data_type
        self.location = location
        self.inchannels = inchannels
        self.outchannels = outchannels

    def create_trace(self, channel, stats, data):
        """Utility to create a new trace object.

        Parameters
        ----------
        channel : str
            channel name.
        stats : obspy.core.Stats
            channel metadata to clone.
        data : numpy.array
            channel data.

        Returns
        -------
        obspy.core.Trace
            trace containing data and metadata.
        """
        stats = Stats(stats)
        if self.data_type is None:
            stats.data_type = 'variation'
        else:
            stats.data_type = self.data_type
        if self.data_type is None:
            stats.location = 'R0'
        else:
            stats.location = self.location

        trace = super(FilterAlgorithm, self).create_trace(channel, stats,
            data)
        return trace

    def process(self, stream):
        """Run algorithm for a stream.
        Processes all traces in the stream.
        Parameters
        ----------
        stream : obspy.core.Stream
            stream of data to process
        Returns
        -------
        out : obspy.core.Stream
            stream containing 1 trace per original trace.
        """

        out = Stream()

        trace_channels = []

        for trace in stream:
            trace_channels += [trace.stats.channel]

        trace_chan_dict1 = dict(zip(self.inchannels, trace_channels))
        print(trace_chan_dict1)
        trace_chan_dict2 = dict(zip(trace_channels, self.outchannels))
        print(trace_chan_dict2)

        for trace in stream:
            data = trace.data
            step = self.decimation

            filtered = self.firfilter(data, self.window, step)

            stats=Stats(trace.stats)
            stats.channel = trace_chan_dict2[stats.channel]
            stats.delta = stats.delta*step
            if 'processing' in stats:
                stats.pop('processing')
            stats.npts = filtered.shape[0]
            trace_out = self.create_trace(
                stats.channel, stats, filtered)

            out += trace_out

        return out

    @staticmethod
    def firfilter(data, window, step, allowed_bad = 0.1):
        """Run fir filter for a numpy array.
        Processes all traces in the stream.
        Parameters
        ----------
        data: numpy.ndarray
            array of data to process
        window: numpy.ndarray
            array of filter coefficients
        step: int
            ratio of output sample period to input sample period
            should always be an integer
        allowed_bad: float
            ratio of bad samples to total window size
        Returns
        -------
        filtered_out : numpy.ndarray
            stream containing filtered output
        """
        numtaps = len(window)

        # build view into data, with numtaps  chunks separated into
        # overlapping 'rows'
        shape = data.shape[:-1] + (data.shape[-1] - numtaps + 1,
                                   numtaps)
        strides = data.strides + (data.strides[-1],)
        as_s = npls.as_strided(data, shape=shape, strides=strides,
                               writeable=False)

        # build masked array for invalid entries, also 'decimate' by step
        as_masked = np.ma.masked_invalid(as_s[::step], copy=True)
        # sums of the total 'weights' of the filter corresponding to
        # valid samples
        as_weight_sums =  np.dot(window, (~as_masked.mask).T)
        # mark the output locations as 'bad' that have missing input weights
        # that sum to greater than the allowed_bad threshhold
        as_invalid_masked = np.ma.masked_less(as_weight_sums, 1 - allowed_bad)

        # apply filter, using masked version of dot (in 3.5 and above, there
        # seems to be a move toward np.matmul and/or @ operator as opposed to
        # np.dot/np.ma.dot - haven't tested to see if the shape of first and
        # second argument need to be changed)
        filtered = np.ma.dot(window, as_masked.T)
        # re-normalize, especially important for partially filled windows
        filtered = np.divide(filtered, as_weight_sums)
        # use the earlier marked output locations to mask the output data
        # array
        filtered.mask = as_invalid_masked.mask
        # convert masked array back to regular array, with nan as fill value
        # (otherwise the type returned is not always the same, and can cause
        # problems with factories, merge, etc.)
        filtered_out = np.ma.filled(filtered, np.nan)

        return filtered_out

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

        half = self.numtaps//2
        start = start - half*self.sample_period
        end = end + half*self.sample_period

        return (start, end)

    @classmethod
    def add_arguments(cls, parser):
        """Add command line arguments to argparse parser.
        Parameters
        ----------
        parser: ArgumentParser
            command line argument parser
        """

        parser.add_argument('--filter-oneminute',
                default=None,
                help='Select one minute filter')

    def configure(self, arguments):
        """Configure algorithm using comand line arguments.
        Parameters
        ----------
        arguments: Namespace
            parsed command line arguments
        """
        pass
