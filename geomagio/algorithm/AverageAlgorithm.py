"""Algorithm that creates an averaged Dst.

"""
from __future__ import absolute_import

from .Algorithm import Algorithm
from .AlgorithmException import AlgorithmException
from ..ObservatoryMetadata import ObservatoryMetadata
import numpy
import obspy.core


# Possible correction factors.
# Defaults to 1.0 if station not found in list.
CORR = {
    'HON': 1.0,
    'SJG': 1.0,
    'HER': 1.0,
    'KAK': 1.0,
    'GUA': 1.0
}


class AverageAlgorithm(Algorithm):
    """Algorithm that creates an averaged Dst.

    Parameters
    ----------

    """

    def __init__(self, observatories=None, channel=None):
        Algorithm.__init__(self)
        self._npts = -1
        self._stt = -1
        self._stats = None
        self.observatories = observatories
        self.outchannel = channel
        self.observatoryMetadata = ObservatoryMetadata()

    def check_stream(self, timeseries):
        """checks a stream to make certain the required data
            exists.

        Parameters
        ----------
        timeseries: obspy.core.Stream
            stream to be checked.
        """

        # A stream produced by EdgeFactory should always pass these checks.

        # must have only one channel for each observatory
        if len(timeseries) != len(self.observatories):
            raise AlgorithmException(
                'Expected data for %d stations, received %d \n'
                    'Only 1 channel may be averaged at one time'
                    % (len(self.observatories), len(timeseries)))

        # timeseries starttime and number of samples must match
        for ts in timeseries:
            # grab 1st set of stats to use in output.
            # Its values will be good if checks pass.
            if self._stats is None:
                self._stats = ts.stats

            if self._npts == -1:
                self._npts = ts.stats.npts
            if ts.stats.npts != self._npts:
                raise AlgorithmException(
                    'Received timeseries have different lengths')

            if self._stt == -1:
                self._stt = ts.stats.starttime
            if ts.stats.starttime != self._stt:
                raise AlgorithmException(
                    'Received timeseries have different starttimes')

    def process(self, timeseries):
        """averages a channel across multiple stations

        Parameters
        ----------

        Returns
        -------
        out_stream:
            new stream object containing the averaged values.
        """

        # If outchannel is not initialized it defaults to the
        # input channel of the timeseries
        if not self.outchannel:
            self.outchannel = timeseries[0].stats.channel

        # Run checks on input timeseries
        self.check_stream(timeseries)

        # initialize array for data to be appended
        combined = []
        # loop over stations
        for obsy in self.observatories:

            # lookup latitude correction factor, default = 1.0
            latcorr = 1.0
            if obsy in CORR:
                latcorr = CORR[obsy]

            # create array of data for each station
            # and take into account correction factor
            ts = timeseries.select(station=obsy)[0]
            combined.append(ts.data * latcorr)

        # after looping over stations, compute average
        dst_tot = numpy.mean(combined, axis=0)

        # Create a stream from the trace function
        stream = obspy.core.Stream((
                get_trace(self.outchannel, self._stats, dst_tot), ))

        # TODO: move this to a better place
        interval = None
        if 'data_interval' in timeseries[0].stats:
            interval = timeseries[0].stats.data_interval
        elif timeseries[0].stats.delta == 60:
            interval = 'minute'
        elif timeseries[0].stats.delta == 1:
            interval = 'second'

        # set the full metadata for the USGS station used for averaged
        # data sets
        self.set_metadata(
            stream=stream,
            observatory='USGS',
            channel=self.outchannel,
            type=stream[0].stats.data_type)

        # return averaged values as a stream
        return stream

    def set_metadata(self, stream, observatory, channel, type, interval):
        """set metadata for a given stream/channel
        Parameters
        ----------
        observatory : str
            observatory code
        channel : str
            edge channel code {MVH, MVE, MVD, ...}
        type : str
            data type {definitive, quasi-definitive, variation}
        interval : str
            interval length {minute, second}
        """

        for trace in stream:
            self.observatoryMetadata.set_metadata(trace.stats, observatory,
                    channel, type, interval)

    @classmethod
    def add_arguments(cls, parser):
        """Add command line arguments to argparse parser.

        Parameters
        ----------
        parser: ArgumentParser
            command line argument parser
        """
        parser.add_argument('--average-observatory-scale',
               default=(None,),
               help='Scale factor for observatories specified with ' +
                    '--observatory argument',
               nargs='*',
               type=float)

    def configure(self, arguments):
        """Configure algorithm using comand line arguments.

        Parameters
        ----------
        arguments: Namespace
            parsed command line arguments
        """

        self.observatories = arguments.observatory
        if arguments.outchannels:
            if len(arguments.outchannels) > 1:
                raise AlgorithmException(
                    'Only 1 channel can be specified')
            self.outchannel = arguments.outchannels[0]

        self.scales = arguments.average_observatory_scale
        if self.scales[0] is not None:
            if len(self.observatories) != len(self.scales):
                raise AlgorithmException(
                    'Mismatch between observatories and scale factors')
            else:
                for (i, obs) in enumerate(self.observatories):
                    CORR[obs] = self.scales[i]


def get_trace(channel, stats, data):
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
    stats = obspy.core.Stats(stats)

    stats.channel = channel
    stats.station = 'USGS'
    stats.network = 'NT'
    stats.location = 'R0'

    return obspy.core.Trace(data, stats)
