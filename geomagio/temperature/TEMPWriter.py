
import numpy
import TEMPParser
from cStringIO import StringIO
from datetime import datetime
from .. import ChannelConverter, TimeseriesUtility
from ..TimeseriesFactoryException import TimeseriesFactoryException
from obspy.core import Stream


class TEMPWriter(object):
    """TEMP writer.
    """

    def __init__(self, empty_value=TEMPParser.NINES_DEG):
        self.empty_value = empty_value

    def write(self, out, timeseries, channels):
        """Write timeseries to temp/volt file.

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
        out.write(self._format_header(stats))
        out.write(self._format_data(timeseries, channels))

    def _format_header(self, stats):
        """format headers for temp/volt file

        Parameters
        ----------
            stats : List
                An object with the header values to be written.

        Returns
        -------
        str
            A string formatted to be a single header line in a temp/volt file.
        """
        buf = []

        observatory = stats.station
        year = str(stats.starttime.year)
        yearday = str(stats.starttime.julday).zfill(3)
        date = stats.starttime.strftime("%d-%b-%y")

        buf.append(observatory + '  ' + year + '  ' + yearday + '  ' + date +
                    '  T1 T2 T3 T4 V1 Deg-C*10/volts*10  File Version 1.00\n')

        return ''.join(buf)

    def _format_data(self, timeseries, channels):
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
            A string formatted to be the data lines in a temp/volt file.
        """
        buf = []

        # create new stream
        timeseriesLocal = Stream()
        # Use a copy of the trace so that we don't modify the original.
        for trace in timeseries:
            traceLocal = trace.copy()

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
                (t.data[i] for t in traces)))

        return ''.join(buf)

    def _format_values(self, time, values):
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
        tt = time.timetuple()
        totalMinutes = int(tt.tm_hour * 60 + tt.tm_min)

        return '{0:0>4d} {1: >5d} {2: >5d} {3: >5d} {4: >5d} {5: >5d}\n'.format(
                totalMinutes,
                *[self.empty_value if numpy.isnan(val) else int(round(
                    val * 10))
                        for val in values])

    @classmethod
    def format(self, timeseries, channels):
        """Get an temp/volt formatted string.

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
          temp/volt formatted string.
        """
        out = StringIO()
        writer = TEMPWriter()
        writer.write(out, timeseries, channels)
        return out.getvalue()
