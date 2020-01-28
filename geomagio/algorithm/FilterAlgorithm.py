from __future__ import absolute_import
from .Algorithm import Algorithm
import numpy as np
from numpy.lib import stride_tricks as npls
import scipy.signal as sps
from obspy.core import Stream, Stats
import json
from .. import TimeseriesUtility as tu


class FilterAlgorithm(Algorithm):
    """
        Filter Algorithm that filters and downsamples data
    """

    def __init__(self, window=None, coeff_filename=None, filtertype=None,
            input_sample_period=None, output_sample_period=None, numtaps=None,
            decimation=None, steparr=None, volt_conv=None, bin_conv=None,
            inchannels=None, outchannels=None):

        Algorithm.__init__(self, inchannels=None, outchannels=None)
        self.window = window
        self.steparr = steparr
        self.coeff_filename = coeff_filename
        self.filtertype = filtertype
        self.numtaps = numtaps
        self.volt_conv = volt_conv
        self.bin_conv = bin_conv
        self.input_sample_period = input_sample_period
        self.output_sample_period = output_sample_period

        # Initialize filter to execute filtering step with custom coefficients
        if self.filtertype == 'custom':
            self.load_state()
            self.numtaps = len(self.window)
        # initialize filter to execute cascading filtering steps
        else:
            self.steparr = np.array([0.1, 1, 60, 3600])
            self.window = [sps.firwin(123, 0.45 / 5.0, window='blackman'),
                    sps.get_window(window=('gaussian', 15.8734), Nx=91),
                    sps.windows.boxcar(91)]
            self.decimation = np.array([1, 10, 60, 60])
            self.numtaps = np.array([123, 91, 91])

        # Set volt/bin conversions to defaults if using Python
        if self.volt_conv is None:
            self.volt_conv = 100
        if self.bin_conv is None:
            self.bin_conv = 500

    def load_state(self):
        """Load algorithm state from a file.
        File name is self.statefile.
        """
        if self.coeff_filename is None:
            return

        data = None

        with open(self.coeff_filename, 'r') as f:
            data = f.read()
            data = json.loads(data)

        if data is None or data == '':
            return

        self.window = np.array(data['window'])

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
        # if input stream is 10 Hz, convert data to nT
        if self.input_sample_period == 0.1:
            stream = self.convert_miniseed(stream)

        output_sample_period = self.output_sample_period
        input_sample_period = self.input_sample_period
        out = Stream()
        # perform one filter operation for custom type filter
        if self.filtertype == 'custom':
            for trace in stream:
                data = trace.data
                step = int(output_sample_period / input_sample_period)
                filtered = self.firfilter(data, self.window, step)
                stats = Stats(trace.stats)
                stats.starttime = trace.stats.starttime + \
                        + self.numtaps * self.input_sample_period // 2 + \
                        + self.input_sample_period
                stats.delta = stats.delta * step
                stats.npts = filtered.shape[0]
                trace_out = self.create_trace(
                        stats.channel, stats, filtered)

                out += trace_out
            return out

        # set stop index to where the sampling period in steparr
        # equals the desired output sample period
        stop_idx = np.argwhere(self.steparr == output_sample_period)[0][0]
        for trace in stream:
            # reinitialize input sample period
            input_sample_period = self.input_sample_period
            # set start index to where the sampling period in steparr
            # equals the desired input sample period
            start_idx = np.argwhere(self.steparr == input_sample_period)[0][0]
            trace_out = trace
            filtered = trace_out.data
            # timeshift value summing all shift to the starttime required in
            # each step to receive desired timeseries
            timeshift = sum(np.array(self.steparr[start_idx:stop_idx]) *
                    (np.array(self.numtaps[start_idx:stop_idx]) // 2))
            while start_idx != stop_idx:
                # set input_sample_period to next filtering step
                input_sample_period = self.steparr[start_idx]
                # set output_sample_period to next filtering step
                output_sample_period = self.steparr[start_idx + 1]
                start_idx += 1
                # select filtering information according to timestep
                step = self.decimation[start_idx]
                window = self.window[start_idx - 1]
                filtered = self.firfilter(filtered, window / sum(window), step)
                stats = Stats(trace.stats)
                # add timeshift value to starttime
                stats.starttime = trace.stats.starttime + timeshift
                # Set delta according to decimation in current time step
                stats.delta = stats.delta * step
                # Set sampling rate according to time step
                stats.sampling_rate = 1 / output_sample_period
                stats.npts = filtered.shape[0]
                # Treat filtered output as new trace
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

    def convert_miniseed(self, stream):
        """Convert miniseed data from bins and volts to nT.
        Converts all traces in stream.
        Parameters
        ----------
        stream: obspy.core.Stream
            stream of data to convert
        Returns
        -------
        out : obspy.core.Stream
            stream containing 1 trace per 2 original traces.
        """
        out = Stream()  # output stream
        # selects volts from input Stream and sorts by channel name
        volts = stream.select(channel="?*V*").sort(['channel'])
        # selects bins from input Stream and sorts by channel name
        bins = stream.select(channel="?*B*").sort(['channel'])
        for i in range(0, len(volts)):
            # copy stats from input trace
            stats = Stats(stream[i].stats)
            # set output trace's channel to U, V, or W
            stats.channel = str(volts[i].stats.channel)[0]
            # convert volts and bins readings into nT data
            data = int(self.volt_conv) * \
            volts[i].data + int(self.bin_conv) * bins[i].data
            # create output trace with adapted channel and data
            trace_out = self.create_trace(stats.channel, stats, data)
            out += trace_out

        return out

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

        if self.filtertype == 'custom':
            self.load_state()
            self.numtaps = len(self.window)
            half = self.numtaps // 2
            start = start - half * self.input_sample_period
            end = end + half * self.input_sample_period
            return (start, end)

        # set start and stop indeces in arrays, which correlate to numtaps
        # and sampling period at each step
        stop_idx = np.argwhere(self.steparr == self.output_sample_period)[0][0]
        start_idx = np.argwhere(self.steparr == self.input_sample_period)[0][0]
        self.numtaps = np.array([123, 91, 91])
        # loop for all time intervals until output interval is reached
        for i in range(start_idx, stop_idx):
            # establish half of the timestep occurs
            half = self.numtaps[i] // 2
            # subtract half the current time step from starttime
            start = start - half * self.steparr[i]
            # add half the current time step from endtime
            end = end + half * self.steparr[i]

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
                help='Specify default filters or custom filter',
                choices=['default', 'custom'])

        parser.add_argument('--filter-coefficients',
                help='File storing custom filter coefficients')

        # conversion factors for volts/bins
        parser.add_argument('--volt-conversion',
                default=100,
                help='Conversion factor for volts')

        parser.add_argument('--bin-conversion',
                default=500,
                help='Conversion factor for bins')

    def configure(self, arguments):
        """Configure algorithm using comand line arguments.
        Parameters
        ----------
        arguments: Namespace
            parsed command line arguments
        """
        Algorithm.configure(self, arguments)

        self.filtertype = arguments.filter_type
        self.volt_conv = arguments.volt_conversion
        self.bin_conv = arguments.bin_conversion
        self.coeff_filename = arguments.filter_coefficients
        input_interval = arguments.input_interval
        output_interval = arguments.output_interval
        self.input_sample_period = tu.get_delta_from_interval(input_interval)
        self.output_sample_period = tu.get_delta_from_interval(output_interval)
