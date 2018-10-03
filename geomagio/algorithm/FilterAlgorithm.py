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
    """Adjusted Data Algorithm"""

    def __init__(self, matrix=None, decimation=None, window=None,
            data_type=None, location=None, inchannels=None, outchannels=None):
        Algorithm.__init__(self, inchannels=inchannels,
            outchannels=outchannels)
        self.numtaps=91
        # get filter window (standard intermagnet one-minute filter)
        self.window = sps.get_window(window=('gaussian', 15.8734), 
                                             Nx=self.numtaps)
        # normalize filter window
        self.window = self.window/np.sum(self.window)
        self.decimation = 60
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
            half = (self.numtaps-1)/2
            step = self.decimation
            shape = data.shape[:-1] + (data.shape[-1] - numtaps + 1, 
                                       numtaps)
            strides = data.strides + (data.strides[-1],)
            as_s = npls.as_strided(data, shape=shape, strides=strides, 
                                   writeable=False)

            filtered = np.dot(self.window, as_s[half:-half:step].T)

            stats=Stats(trace.stats)
            stats.delta = delta*self.decimation
            stats.npts = len(filtered)
            trace_out = self.create_trace('', trace.stats)

            out += trace_out

        return out

    @classmethod
    def add_arguments(cls, parser):
        """Add command line arguments to argparse parser.
        Parameters
        ----------
        parser: ArgumentParser
            command line argument parser
        """

        parser.add_argument('--adjusted-statefile',
                default=None,
                help='File to store state between calls to algorithm')

    def configure(self, arguments):
        """Configure algorithm using comand line arguments.
        Parameters
        ----------
        arguments: Namespace
            parsed command line arguments
        """
        Algorithm.configure(self, arguments)
        self.statefile = arguments.adjusted_statefile
        self.load_state()
