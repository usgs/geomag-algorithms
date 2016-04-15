"""Algorithm that converts from one geomagnetic coordinate system to a
    related geographic coordinate system, by using transformations generated
    from absolute, baseline measurements.
"""
from Algorithm import Algorithm
import json
import numpy as np
from obspy.core import Stream, Stats


class AdjustedAlgorithm(Algorithm):
    """Adjusted Data Algorithm"""

    def __init__(self, matrix=None, pier_correction=None, statefile=None):
        Algorithm.__init__(self, inchannels=('H', 'E', 'Z', 'F'),
            outchannels=('X', 'Y', 'Z', 'F'))
        # state variables
        self.matrix = matrix
        self.pier_correction = pier_correction
        self.statefile = statefile
        self.load_state()

    def load_state(self):
        """Load algorithm state from a file.
        File name is self.statefile.
        """
        self.matrix = np.eye(4)
        self.pier_correction = 0
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
        self.matrix[0, 0] = np.float64(data['M11'])
        self.matrix[0, 1] = np.float64(data['M12'])
        self.matrix[0, 2] = np.float64(data['M13'])
        self.matrix[0, 3] = np.float64(data['M14'])
        self.matrix[1, 0] = np.float64(data['M21'])
        self.matrix[1, 1] = np.float64(data['M22'])
        self.matrix[1, 2] = np.float64(data['M23'])
        self.matrix[1, 3] = np.float64(data['M24'])
        self.matrix[2, 0] = np.float64(data['M31'])
        self.matrix[2, 1] = np.float64(data['M32'])
        self.matrix[2, 2] = np.float64(data['M33'])
        self.matrix[2, 3] = np.float64(data['M34'])
        self.matrix[3, 0] = np.float64(data['M41'])
        self.matrix[3, 1] = np.float64(data['M42'])
        self.matrix[3, 2] = np.float64(data['M43'])
        self.matrix[3, 3] = np.float64(data['M44'])
        self.pier_correction = np.float64(data['PC'])

    def save_state(self):
        """Save algorithm state to a file.
        File name is self.statefile.
        """
        if self.statefile is None:
            return
        data = {
            'M11': self.matrix[0, 0],
            'M12': self.matrix[0, 1],
            'M13': self.matrix[0, 2],
            'M14': self.matrix[0, 3],
            'M21': self.matrix[1, 0],
            'M22': self.matrix[1, 1],
            'M23': self.matrix[1, 2],
            'M24': self.matrix[1, 3],
            'M31': self.matrix[2, 0],
            'M32': self.matrix[2, 1],
            'M33': self.matrix[2, 2],
            'M34': self.matrix[2, 3],
            'M41': self.matrix[3, 0],
            'M42': self.matrix[3, 1],
            'M43': self.matrix[3, 2],
            'M44': self.matrix[3, 3],
            'PC': self.pier_correction
        }
        with open(self.statefile, 'w') as f:
            f.write(json.dumps(data))

    @classmethod
    def create_trace(cls, channel, stats, data):
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
        stats.data_type = 'adjusted'
        stats.location = 'A0'
        Trace = super(AdjustedAlgorithm, cls).create_trace(channel, stats,
            data)
        return Trace

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
            stream containing 1 trace per original trace. (h->X, e->Y, z->Z)
        """

        out = None

        h = stream.select(channel='H')[0]
        e = stream.select(channel='E')[0]
        z = stream.select(channel='Z')[0]
        f = stream.select(channel='F')[0]

        raws = np.vstack([h.data, e.data, z.data, np.ones_like(h.data)])
        adj = np.dot(self.matrix, raws)
        fnew = f.data + self.pier_correction

        x = self.create_trace('X', h.stats, adj[0])
        y = self.create_trace('Y', e.stats, adj[1])
        z = self.create_trace('Z', z.stats, adj[2])
        f = self.create_trace('F', f.stats, fnew)

        out = Stream([x, y, z, f])

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
