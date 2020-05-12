from .Algorithm import Algorithm
from ..TimeseriesUtility import create_empty_trace, get_interval_from_delta

import numpy as np
from obspy.core import Stream, Stats


class DbDtAlgorithm(Algorithm):
    def __init__(self, inchannels=None, outchannels=None, interval=None):
        """
        Derivative algorithm that takes derivative of timeseries using second order central differences(numpy.gradient)
        """
        Algorithm.__init__(self, inchannels=None, outchannels=None)
        self.inchannels = inchannels
        self.outchannels = outchannels
        self.interval = interval

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
            dbdt = np.diff(trace.data)
            stats = Stats(trace.stats)
            stats.channel = "{}__DDT".format(stats.channel)
            trace_out = create_empty_trace(
                starttime=stats.starttime + self.interval,
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

    def get_interval(self, start):
        """
        Adjust time interval for input data.
        Parameters
        ----------
        end : obspy.core.UTCDatetime
            input endtime
        Returns
        -------
        end : obspy.core.UTCDatetime
            output endtime
        """
        start -= self.interval
        return start
