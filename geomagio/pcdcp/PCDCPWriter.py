
import numpy
import PCDCPParser
from cStringIO import StringIO
from datetime import datetime
from .. import ChannelConverter, TimeseriesUtility
from ..TimeseriesFactoryException import TimeseriesFactoryException
from obspy.core import Stream


class PCDCPWriter(object):
    """PCDCP writer.
    """

    def __init__(self, empty_value=PCDCPParser.NINES):
        self.empty_value = empty_value

    def write(self, out, timeseries, channels):
        """Write timeseries to pcdcp file.

        Parameters
        ----------
            out : file object
                File object to be written to. Could be stdout.
            timeseries : obspy.core.stream
                Timeseries object with data to be written.
            channels : array_like
                Channels to be written from timeseries object.
        """
        for channel in channels:
            if timeseries.select(channel=channel).count() == 0:
                raise TimeseriesFactoryException(
                    'Missing channel "%s" for output, available channels %s' %
                    (channel, str(TimeseriesUtility.get_channels(timeseries))))
        stats = timeseries[0].stats

        # Set dead val for 1-sec data.
        # Won't work if input is IAGA2002: stats missing data_interval
        if stats.data_interval == "second":
            self.empty_value = PCDCPParser.NINES_RAW

        out.write(self._format_header(stats))

        out.write(self._format_data(timeseries, channels, stats))

    def _format_header(self, stats):
        """format headers for PCDCP file

        Parameters
        ----------
            stats : List
                An object with the header values to be written.

        Returns
        -------
        str
            A string formatted to be a single header line in a PCDCP file.
        """
        buf = []

        observatory = stats.station
        year = str(stats.starttime.year)
        yearday = str(stats.starttime.julday).zfill(3)
        date = stats.starttime.strftime("%d-%b-%y")

        # Choose resolution for 1-sec vs 1-min header.
        resolution = "0.01nT"
        # won't work if input is IAGA2002: stats missing data_interval
        if stats.data_interval == "second":
            resolution = "0.001nT"

        buf.append(observatory + '  ' + year + '  ' + yearday + '  ' +
                    date + '  HEZF  ' + resolution + '  File Version 2.00\n')

        return ''.join(buf)

    def _format_data(self, timeseries, channels, stats):
        """Format all data lines.

        Parameters
        ----------
            timeseries : obspy.core.Stream
                Stream containing traces with channel listed in channels
            channels : sequence
                List and order of channel values to output.

        Returns
        -------
        str
            A string formatted to be the data lines in a PCDCP file.
        """
        buf = []

        # create new stream
        timeseriesLocal = Stream()
        # Use a copy of the trace so that we don't modify the original.
        for trace in timeseries:
            traceLocal = trace.copy()
            if traceLocal.stats.channel == 'D':
                traceLocal.data = \
                    ChannelConverter.get_minutes_from_radians(traceLocal.data)

            # TODO - we should look into multiplying the trace all at once
            # like this, but this gives an error on Windows at the moment.
            # traceLocal.data = \
            #     numpy.round(numpy.multiply(traceLocal.data, 100)).astype(int)

            timeseriesLocal.append(traceLocal)

        traces = [timeseriesLocal.select(channel=c)[0] for c in channels]
        starttime = float(traces[0].stats.starttime)
        delta = traces[0].stats.delta

        for i in xrange(len(traces[0].data)):
            buf.append(self._format_values(
                datetime.utcfromtimestamp(starttime + i * delta),
                (t.data[i] for t in traces), stats))

        return ''.join(buf)

    def _format_values(self, time, values, stats):
        """Format one line of data values.

        Parameters
        ----------
            time : datetime
                Timestamp for values.
            values : sequence
                List and order of channel values to output.
                If value is NaN, self.empty_value is output in its place.

        Returns
        -------
        unicode
            Formatted line containing values.
        """
        # 1-sec and 1-min data have different formats.
        # Won't work if input is IAGA2002: stats missing data_interval.
        time_width = 4
        data_width = 8
        data_multiplier = 100
        hr_multiplier = 60
        mn_multiplier = 1
        sc_multiplier = 0
        if stats.data_interval == "second":
            time_width = 5
            data_width = 9
            data_multiplier = 1000
            hr_multiplier = 3600
            mn_multiplier = 60
            sc_multiplier = 1

        tt = time.timetuple()

        totalMinutes = int(tt.tm_hour * hr_multiplier +
                        tt.tm_min * mn_multiplier + tt.tm_sec * sc_multiplier)

        return '{0:0>{tw}d} {1: >{dw}d} {2: >{dw}d} {3: >{dw}d}' \
                ' {4: >{dw}d}\n'.format(totalMinutes, tw=time_width,
                *[self.empty_value if numpy.isnan(val) else int(round(
                    val * data_multiplier))
                        for val in values], dw=data_width)

    @classmethod
    def format(self, timeseries, channels):
        """Get an PCDCP formatted string.

        Calls write() with a StringIO, and returns the output.

        Parameters
        ----------
            timeseries : obspy.core.Stream
                Stream containing traces with channel listed in channels
            channels : sequence
                List and order of channel values to output.

        Returns
        -------
        unicode
          PCDCP formatted string.
        """
        out = StringIO()
        writer = PCDCPWriter()
        writer.write(out, timeseries, channels)
        return out.getvalue()
