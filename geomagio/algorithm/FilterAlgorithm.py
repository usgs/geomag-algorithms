from __future__ import absolute_import
from .Algorithm import Algorithm
import numpy as np
from numpy.lib import stride_tricks as npls
from obspy.core import Stream, Stats
import json
from .. import TimeseriesUtility as tu


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

    def load_state(self):
        """Load algorithm state from json file if default steps are used.
        Create dictionary object if custom filter is used.
        File name is steps.json.
        """
        input_sample_period = self.input_sample_period
        output_sample_period = self.output_sample_period

        if self.filtertype == 'default' or self.filtertype is None:
            # load json file holding step information
            data = json.load(open('geomagio/algorithm/steps.json'))
            # match input interval to string
            if input_sample_period == 0.1:
                start_string = 'tenhertz'
            elif input_sample_period == 1.0:
                start_string = 'second'
            elif input_sample_period == 60.0:
                start_string = 'minute'
            # match output interval to string
            if output_sample_period == 1.0:
                stop_string = 'second'
            elif output_sample_period == 60.0:
                stop_string = 'minute'
            elif output_sample_period == 3600:
                stop_string = 'hour'

            # make keys from dictionary iterable
            keys = np.array(list(data.keys()))

            for i in range(len(keys)):
                # split step name into input and output sample periods
                first, second = keys[i].split('_')
                # get matching step indeces to access from dictionary
                if second == stop_string:
                    start_idx = i
                if first == start_string:
                    stop_idx = i

            steps = dict()
            # gather timesteps needed for filter
            for i in keys[start_idx:stop_idx + 1]:
                first, second = i.split('_')
                json_string_first = first
                json_string_second = second
                load_string = json_string_first + '_' + json_string_second
                steps[load_string] = data[load_string]
        # initialize dictionary for custom filter
        if self.filtertype == 'custom':
            steps = dict()
            steps["input_sample_period"] = input_sample_period
            steps["output_sample_period"] = output_sample_period
            decimation = output_sample_period // input_sample_period
            steps["decimation"] = int(decimation)
            # loads coeffs from json file
            if self.coeff_filename is None:
                return

            with open(self.coeff_filename, 'r') as f:
                data = f.read()
                data = json.loads(data)

            if data is None or data == '':
                return

            steps["window"] = list(data["window"])
        self.steps = steps

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
        # intitialize dictionary object for default or custom filter
        self.load_state()
        steps = self.steps
        out_stream = Stream()
        out_stream = stream.copy()
        # while dictionary is not empty
        while steps:
            # removes filtering step from dictionary for one step
            if self.filtertype == 'default' or self.filtertype is None:
                step = steps.popitem()[1]
            # custom filter uses a one element dictionary
            # sets dictionary to empty to exit loop after one step
            if self.filtertype == 'custom':
                step = steps
                steps = dict()
            # gather variables from single step
            window = np.array(step["window"])
            numtaps = len(window)
            input_sample_period = step["input_sample_period"]
            output_sample_period = step["output_sample_period"]
            decimation = step["decimation"]
            out = Stream()
            # from original algorithm
            for trace in out_stream:
                data = trace.data
                filtered = self.firfilter(data,
                        window / sum(window), decimation)
                stats = Stats(trace.stats)
                stats.starttime = stats.starttime + \
                        input_sample_period * (numtaps // 2)
                stats.sampling_rate = 1 / output_sample_period
                stats.delta = output_sample_period
                stats.npts = filtered.shape[0]
                trace_out = self.create_trace(stats.channel, stats, filtered)
                out += trace_out
            # set out_stream to filtered output and continue while loop
            out_stream = out.copy()
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
        self.load_state()
        steps = self.steps
        # if custom filter is used, calculate start/end
        # from single element dictionary
        if self.filtertype == 'custom':
            half = len(steps["window"]) // 2
            start = start - half * steps["input_sample_period"]
            end = end + half * steps["input_sample_period"]
            return (start, end)
        # if default filter is used, calculate start/end
        # from multiple-element dictionary
        for i in sorted(steps.keys(), reverse=True):
            half = len(steps[i]["window"]) // 2
            start = start - half * steps[i]["input_sample_period"]
            end = end + half * steps[i]["input_sample_period"]
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

        parser.add_argument('--filter-type',
                default=None,
                help='Specify default filters or custom filter',
                choices=['default', 'custom'])

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
        self.filtertype = arguments.filter_type
        self.coeff_filename = arguments.filter_coefficients
        input_interval = arguments.input_interval
        output_interval = arguments.output_interval
        self.input_sample_period = tu.get_delta_from_interval(input_interval)
        self.output_sample_period = tu.get_delta_from_interval(output_interval)
