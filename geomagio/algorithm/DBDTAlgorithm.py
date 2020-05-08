from __future__ import absolute_import
from ..TimeseriesUtility import create_empty_trace, get_interval_from_delta
from .Algorithm import Algorithm
import numpy as np
from obspy.core import Stream, Stats


class DBDTAlgorithm(Algorithm):
    def __init__(self, inchannels=None, outchannels=None):
        """
        Derivative algorithm that takes derivative of timeseries using second order central differences(numpy.gradient)
        """
        Algorithm.__init__(self, inchannels=None, outchannels=None)
        self.inchannels = inchannels
        self.outchannels = outchannels

    def process(self, stream):
        """
        Run algorithm for a stream.
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
            dbdt = np.gradient(trace.data)
            stats = Stats(trace.stats)
            stats.channel = "DBDT-" + stats.channel
            trace_out = create_empty_trace(
                starttime=stats.starttime,
                endtime=stats.endtime,
                observatory=stats.station,
                type=stats.location,
                interval=get_interval_from_delta(stats.delta),
                channel=stats.channel,
                network=stats.network,
                station=stats.station,
                location=stats.location,
            )
            trace_out.data = dbdt
            out += trace_out
        return out
