from __future__ import absolute_import
from .Algorithm import Algorithm
import numpy as np
import scipy.signal as sps
from numpy.lib import stride_tricks as npls
from obspy.core import Stream, Stats
import json
from ..TimeseriesUtility import get_delta_from_interval


STEPS = [
    {  # 10 Hz to one second filter
        'name': '10Hz',
        'input_sample_period': 0.1,
        'output_sample_period': 1.0,
        'window': sps.firwin(123, 0.45 / 5.0, window='blackman'),
    },

    {  # one second to one minute filter
        'name': 'Intermagnet One Minute',
        'input_sample_period': 1.0,
        'output_sample_period': 60.0,
        'window': sps.get_window(window=('gaussian', 15.8734), Nx=91),
    },

    {  # one minute to one hour filter
        'name': 'One Hour',
        'input_sample_period': 60.0,
        'output_sample_period': 3600.0,
        'window': sps.windows.boxcar(91),
    }
        ]


class FilterAlgorithm(Algorithm):
    """
        Filter Algorithm that filters and downsamples data
    """

    def __init__(self, coeff_filename=None, filtertype=None,
            steps=None, input_sample_period=None, output_sample_period=None,
            inchannels=None, outchannels=None):

        Algorithm.__init__(self, inchannels=None, outchannels=None)
        self.coeff_filename = coeff_filename
        self.filtertype = filtertype
        self.input_sample_period = input_sample_period
        self.output_sample_period = output_sample_period
        self.steps = steps
        self.load_state()

    def load_state(self):
        """Load filter coefficients from json file if custom filter is used.
        File name is self.coeff_filename.
        """
        if self.coeff_filename is None:
            return

        with open(self.coeff_filename, 'r') as f:
            data = f.read()
            data = json.loads(data)

        if data is None or data == '':
            return

        self.steps = [{
            'name': 'name' in data and data['name'] or 'custom',
            'input_sample_period': self.input_sample_period,
            'output_sample_period': self.output_sample_period,
            'window': data['window']
        }]

    def save_state(self):
        """Save algorithm state to a file.
        File name is self.statefile.
        """
        if self.coeff_filename is None:
            return
        data = {
            'window': list(self.window)
        }
        with open(self.coeff_filename, 'w') as f:
            f.write(json.dumps(data))

    def get_filter_steps(self):
        """Method to gather necessary filtering steps from STEPS constant.
        Returns
        -------
        list
            Returns list of filter steps.
            Steps can be passed in constructor as an array as steps.

        """
        if self.steps:
            return self.steps

        steps = []
        for step in STEPS:
            if self.input_sample_period <= step['input_sample_period']:
                if self.output_sample_period >= step['output_sample_period']:
                    steps.append(step)
        return steps

    def create_trace(self, channel, stats, data):
        """Utility to create a new trace object.
        This may be necessary for more sophisticated metadata
        modifications, but for now it simply passes inputs back
        to parent Algorithm class.
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
        # intitialize step array for filter
        steps = self.get_filter_steps()
        for step in steps:
            stream = self.process_step(step, stream.copy())

        return stream

    def process_step(self, step, stream):
        """Filters stream for one step.
        Filters all traces in stream.
        Parameters
        ----------
        step : array element
            step holding variables for one filtering operation
        stream : obspy.core.Stream
            stream of data to filter
        Returns
        -------
        out : obspy.core.Stream
            stream containing 1 trace per original trace.
        """
        # gather variables from step
        input_sample_period = step['input_sample_period']
        output_sample_period = step['output_sample_period']
        window = np.array(step['window'])
        decimation = int(output_sample_period / input_sample_period)
        numtaps = len(window)
        window = window / sum(window)

        out = Stream()
        for trace in stream:
            filtered = self.firfilter(trace.data,
                    window, decimation)
            stats = Stats(trace.stats)
            stats.starttime = stats.starttime + \
                    input_sample_period * (numtaps // 2)
            stats.delta = output_sample_period
            stats.npts = len(filtered)
            trace_out = self.create_trace(stats.channel, stats, filtered)
            out += trace_out
        return out

    @staticmethod
    def firfilter(data, window, step, allowed_bad=0.1):
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
        shape = data.shape[:-1] + \
                (data.shape[-1] - numtaps + 1, numtaps)
        strides = data.strides + (data.strides[-1],)
        as_s = npls.as_strided(data, shape=shape, strides=strides,
                               writeable=False)
        # build masked array for invalid entries, also 'decimate' by step
        as_masked = np.ma.masked_invalid(as_s[::step], copy=True)
        # sums of the total 'weights' of the filter corresponding to
        # valid samples
        as_weight_sums = np.dot(window, (~as_masked.mask).T)
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
        steps = self.get_filter_steps()
        # calculate start/end from step array
        for step in steps:
            half = len(step["window"]) // 2
            half_step = half * step["input_sample_period"]
            start = start - half_step
            end = end + half_step
        return (start, end)

    @classmethod
    def add_arguments(cls, parser):
        """Add command line arguments to argparse parser.
        Parameters
        ----------
        parser: ArgumentParser
            command line argument parser
        """
        # input and output time intervals are managed
        # by Controller and TimeriesUtility

        parser.add_argument('--filter-coefficients',
                default=None,
                help='File storing custom filter coefficients')

    def configure(self, arguments):
        """Configure algorithm using comand line arguments.
        Parameters
        ----------
        arguments: Namespace
            parsed command line arguments
        """
        Algorithm.configure(self, arguments)
        # intialize filter with command line arguments
        self.coeff_filename = arguments.filter_coefficients
        input_interval = arguments.input_interval
        output_interval = arguments.output_interval
        self.input_sample_period = get_delta_from_interval(input_interval)
        self.output_sample_period = get_delta_from_interval(output_interval)
        self.load_state()
