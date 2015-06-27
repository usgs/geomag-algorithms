
from cStringIO import StringIO
from geomagio import ChannelConverter
import numpy
import PCDCPParser
from datetime import datetime


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
        stats = timeseries[0].stats
        out.write(self._format_header(stats))
        out.write(self._format_data(timeseries, channels))

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

        buf.append(observatory + '  ' + year + '  ' + yearday + '  ' +
                    date + '  HEZF  0.01nT  File Version 2.00\n')

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
            A string formatted to be the data lines in a PCDCP file.
        """
        buf = []

        # Use a copy of the trace so that we don't modify the original.
        timeseriesLocal = timeseries.copy()

        if timeseriesLocal.select(channel='D'):
            d = timeseriesLocal.select(channel='D')
            d[0].data = ChannelConverter.get_minutes_from_radians(d[0].data)

        # TODO - is this doing anything?
        i = 0
        for trace in timeseriesLocal:
            timeseriesLocal[i].trace = numpy.round(numpy.multiply(trace, 100))
            i += 1

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

        return '{0:0>4d} {2: >8d} {3: >8d} {4: >8d} {5: >8d}\n'.format(
                totalMinutes, int(time.microsecond / 1000),
                *[self.empty_value if numpy.isnan(val) else int(round(val*100))
                        for val in values])

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
