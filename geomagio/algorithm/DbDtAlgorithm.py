from .Algorithm import Algorithm
from ..TimeseriesUtility import (
    create_empty_trace,
    get_interval_from_delta,
    get_delta_from_interval,
)

import numpy as np
from obspy.core import Stream, Stats


class DbDtAlgorithm(Algorithm):
    def __init__(self, inchannels=None, outchannels=None, period=None):
        """
        Derivative algorithm that takes derivative of timeseries using second order central differences(numpy.gradient)
        """
        Algorithm.__init__(self, inchannels=None, outchannels=None)
        self.inchannels = inchannels
        self.outchannels = outchannels
        self.period = period

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
            dbdt = np.around(np.diff(trace.data), decimals=6)
            stats = Stats(trace.stats)
            stats.channel = "{}_DT".format(stats.channel)
            trace_out = create_empty_trace(
                starttime=stats.starttime + stats.delta,
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

    def get_input_interval(self, start, end, observatory=None, channels=None):
        """
        Adjust time interval for input data.
        Parameters
        ----------
        start : obspy.core.UTCDatetime
            input starttime
        end : obspy.core.UTCDatetime
            input endtime
        Returns
        -------
        start : obspy.core.UTCDatetime
            output starttime
        end : obspy.core.UTCDatetime
            output endtime
        """
        start -= self.period
        return (start, end)

    def configure(self, arguments):
        """Configure algorithm using comand line arguments.
        Parameters
        ----------
        arguments: Namespace
            parsed command line arguments
        """
        self.period = get_delta_from_interval(arguments.interval)
