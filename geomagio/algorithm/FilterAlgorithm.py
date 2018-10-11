"""Algorithm that converts from one geomagnetic coordinate system to a
    related geographic coordinate system, by using transformations generated
    from absolute, baseline measurements.
"""
from __future__ import absolute_import

from .Algorithm import Algorithm
import json
import numpy as np
from numpy.lib import stride_tricks as npls
import scipy.signal as sps
from obspy.core import Stream, Stats
import sys


class FilterAlgorithm(Algorithm):
    """Filter Algorithm"""

    def __init__(self, decimation=None, window=None, interval=None, 
                 location=None, inchannels=None, outchannels=None):
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

        for trace in stream:
            data = trace.data
            times = trace.times()
            half = self.numtaps//2
            step = self.decimation

            filtered = self.firfilter(data, self.window, half)

            stats=Stats(trace.stats)
            stats.delta = trace.delta*step
            stats.npts = len(filtered)
            trace_out = self.create_trace('', trace.stats, filtered_out)

            out += trace_out

        return out
    
    @classmethod
    def firfilter(cls, data, window, step, allowed_bad = 0.1):
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
        half = numtaps // 2

        # build view into data, with numtaps  chunks separated into 
        # overlapping 'rows'
        shape = data.shape[:-1] + (data.shape[-1] - numtaps + 1, 
                                   numtaps)
        
        strides = data.strides + (data.strides[-1],)
        
        as_s = npls.as_strided(data, shape=shape, strides=strides, 
                               writeable=False)
            
        # build masked array for invalid entries
        as_masked = np.ma.masked_invalid(as_s[half:-half:step], copy=True)
        as_weight_sums =  np.dot(window, (~as_masked.mask).T)
        as_invalid_sums = np.sum(as_masked.mask)
            
        as_invalid_masked = np.ma.masked_greater(as_invalid_sums, 
                                                 np.floor(
                                                    allowed_bad*numtaps))

        # apply filter
        filtered = np.ma.dot(window, as_masked.T)
        # re-normalize, especially important for partially filled windows
        filtered = np.divide(filtered, as_weight_sums)
        filtered.mask = as_invalid_masked.mask
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
        step = self.decimation
        start = start - half*self.interval
        end = end + half*self.interval

        return (start, end)
