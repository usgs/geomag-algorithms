"""Algorithm that converts from one geomagnetic coordinate system to a
    related geographic coordinate system, by using transformations generated
    from absolute, baseline measurements.
"""
from __future__ import absolute_import

from .Algorithm import Algorithm
import json
import numpy as np
from obspy.core import Stream, Stats
import sys


class AdjustedAlgorithm(Algorithm):
    """Adjusted Data Algorithm"""

    def __init__(
        self,
        matrix=None,
        pier_correction=None,
        statefile=None,
        data_type=None,
        location=None,
        inchannels=None,
        outchannels=None,
    ):
        Algorithm.__init__(self, inchannels=None, outchannels=None)
        # state variables
        self.matrix = matrix
        self.pier_correction = pier_correction
        self.statefile = statefile
        self.data_type = data_type
        self.location = location
        self.inchannels = inchannels
        self.outchannels = outchannels
        if matrix is None:
            self.load_state()

    def load_state(self):
        """Load algorithm state from a file.
        File name is self.statefile.
        """
        self.matrix = None
        self.pier_correction = 0
        if self.statefile is None:
            return
        data = None
        try:
            with open(self.statefile, "r") as f:
                data = f.read()
                data = json.loads(data)
        except IOError as err:
            sys.stderr.write("I/O error {0}".format(err))
        if data is None or data == "":
            return

        PC = data.pop("PC")
        self.pier_correction = np.float64(PC)
        # excludes PC
        keys = list(data.keys())
        # get maximum row/colum number
        length = int(max(keys)[-1])
        self.matrix = np.eye(length)
        for i in range(length):
            for j in range(length):
                key = "M" + str(i + 1) + str(j + 1)
                self.matrix[i, j] = np.float64(data[key])

    def save_state(self):
        """Save algorithm state to a file.
        File name is self.statefile.
        """
        if self.statefile is None:
            return
        data = {"PC": self.pier_correction}

        length = len(self.matrix[0, :])

        for i in range(length):
            for j in range(length):
                key = "M" + str(i + 1) + str(j + 1)
                data[key] = self.matrix[i, j]

        with open(self.statefile, "w") as f:
            f.write(json.dumps(data))

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
            stats.data_type = "adjusted"
        else:
            stats.data_type = self.data_type
        if self.data_type is None:
            stats.location = "A0"
        else:
            stats.location = self.location

        trace = super(AdjustedAlgorithm, self).create_trace(channel, stats, data)
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
            stream containing 1 trace per original trace. (h, e, z)->(X, Y, Z)
        """

        out = None
        inchannels = self.inchannels
        outchannels = self.outchannels
        # Gather input traces in order of user input(inchannels)
        raws = [
            stream.select(channel=channel) for channel in inchannels if channel != "F"
        ]
        # Append aray of ones as for affine matrix
        raws.append(np.ones_like(stream[0].data))
        raws = np.vstack(raws)
        adj = np.matmul(self.matrix, raws)[:-1]
        if "F" in inchannels:
            f = stream.select(channel="F")[0]
            fnew = f.data + self.pier_correction
            adj = np.vstack((adj, fnew))

        out = Stream()
        # Create new steam with adjusted data in order of user input(outchannels)
        for i in range(len(stream)):
            trace = stream[i]
            data = adj[i]
            channel = outchannels[i]
            out += self.create_trace(channel, trace.stats, data)

        return out

    def can_produce_data(self, starttime, endtime, stream):
        """Can Product data
        Parameters
        ----------
        starttime: UTCDateTime
            start time of requested output
        end : UTCDateTime
            end time of requested output
        stream: obspy.core.Stream
            The input stream we want to make certain has data for the algorithm
        """

        channels = self.inchannels

        # if F is available, can produce at least adjusted F
        if "F" in channels and super(AdjustedAlgorithm, self).can_produce_data(
            starttime, endtime, stream.select(channel="F")
        ):
            return True

        # if HEZ are available, can produce at least adjusted XYZ
        if (
            "H" in channels
            and "E" in channels
            and "Z" in channels
            and np.all(
                [
                    super(AdjustedAlgorithm, self).can_produce_data(
                        starttime, endtime, stream.select(channel=chan)
                    )
                    for chan in ("H", "E", "Z")
                ]
            )
        ):
            return True

        # If being used for another conversion, check if all channels can produce data
        if np.all(
            [
                super(AdjustedAlgorithm, self).can_produce_data(
                    starttime, endtime, stream.select(channel=chan)
                )
                for chan in channels
            ]
        ):
            return True

        # return false if cannot produce adjustded F or XYZ
        return False

    @classmethod
    def add_arguments(cls, parser):
        """Add command line arguments to argparse parser.
        Parameters
        ----------
        parser: ArgumentParser
            command line argument parser
        """

        parser.add_argument(
            "--adjusted-statefile",
            default=None,
            help="File to store state between calls to algorithm",
        )

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
