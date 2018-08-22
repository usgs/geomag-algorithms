"""Algorithm that creates an averaged Dst.

"""
from __future__ import absolute_import

from .Algorithm import Algorithm
from .AlgorithmException import AlgorithmException
from ..ObservatoryMetadata import ObservatoryMetadata
import numpy
import obspy.core


class AverageAlgorithm(Algorithm):
    """Algorithm that creates an averaged Dst.

    Parameters
    ----------

    """

    def __init__(self, observatories=None, channel=None, scales=None):
        Algorithm.__init__(self)
        self._npts = -1
        self._stt = -1
        self._stats = None
        self.scales = scales
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

        first = True
        # timeseries starttime and number of samples must match
        for ts in timeseries:
            # grab 1st set of stats to use in output.
            # Its values will be good if checks pass.
            if first:
                self._stats = ts.stats
                self._npts = ts.stats.npts
                self._stt = ts.stats.starttime
                first = False

            if ts.stats.npts != self._npts:
                raise AlgorithmException(
                    'Received timeseries have different lengths')

            if numpy.isnan(ts.data).all():
                raise AlgorithmException(
                    'Trace for %s observatory is completely empty.'
                    % (ts.stats.station))

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
        if not self.observatories:
            self.observatories = self.observatories or \
                    [t.stats.station for t in timeseries]

        if not self.outchannel:
            self.outchannel = timeseries[0].stats.channel

        scale_values = self.scales or ([1] * len(timeseries))
        lat_corr = {}
        i = 0
        for obs in self.observatories:
            new_obs = {str(obs): scale_values[i]}
            lat_corr.update(new_obs)
            i += 1

        # Run checks on input timeseries
        self.check_stream(timeseries)

        # initialize array for data to be appended
        combined = []
        # loop over stations
        for obsy in self.observatories:

            # lookup latitude correction factor, default = 1.0
            if obsy in lat_corr:
                latcorr = lat_corr[obsy]

            # create array of data for each station
            # and take into account correction factor
            ts = timeseries.select(station=obsy)[0]
            combined.append(ts.data * latcorr)

        # after looping over stations, compute average
        dst_tot = numpy.mean(combined, axis=0)

        # Create a stream from the trace function
        new_stats = obspy.core.Stats()
        new_stats.station = 'USGS'
        new_stats.channel = self.outchannel
        new_stats.network = 'NT'
        new_stats.location = 'RD'
        new_stats.starttime = timeseries[0].stats.starttime
        new_stats.npts = timeseries[0].stats.npts
        new_stats.delta = timeseries[0].stats.delta
        stream = obspy.core.Stream((
                obspy.core.Trace(dst_tot, new_stats), ))

        # return averaged values as a stream
        return stream

    @classmethod
    def add_arguments(cls, parser):
        """Add command line arguments to argparse parser.

        Parameters
        ----------
        parser: ArgumentParser
            command line argument parser
        """
        parser.add_argument('--average-observatory-scale',
               default=None,
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
        if self.scales:
            if len(self.observatories) != len(self.scales):
                raise AlgorithmException(
                    'Mismatch between observatories and scale factors')
