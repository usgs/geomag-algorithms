
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
        out.write(self._format_header(stats, channels))
        out.write(self._format_data(timeseries, channels))

    def _format_header(self, name, value):
        """format headers for PCDCP file

        Parameters
        ----------
        name : str
            the name to be written
        value : str
            the value to written.

        Returns
        -------
        str
            a string formatted to be a single header line in a PCDCP file
        """
        buf = []
        observatory = name.station
        year = str(name.starttime.year)
        yearday = str(name.starttime.julday).zfill(3)
        date = name.starttime.strftime("%d-%b-%y")
        space = '  '
        buf.append(observatory + '  ' + year + '  ' + yearday + '  ' +
                    date + '  HEZF  0.01nT  File Version 2.00\n')

        return ''.join(buf)

    def _format_data(self, timeseries, channels):
        """Format all data lines.

        Parameters
        ----------
        timeseries : obspy.core.Stream
            stream containing traces with channel listed in channels
        channels : sequence
            list and order of channel values to output.
        """
        buf = []
        if timeseries.select(channel='D'):
            d = timeseries.select(channel='D')
            d[0].data = ChannelConverter.get_minutes_from_radians(d[0].data)

        traces = [timeseries.select(channel=c)[0] for c in channels]
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
            timestamp for values
        values : sequence
            list and order of channel values to output.
            if value is NaN, self.empty_value is output in its place.

        Returns
        -------
        unicode
            Formatted line containing values.
        """
        tt = time.timetuple()
        totalMinutes = int(tt.tm_hour * 60 + tt.tm_min)
        return '{0:0>4d} ' \
                '{2: >8d} {3: >8d} {4: >8d} {5: >8d}\n'.format(
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

        Returns
        -------
        unicode
          PCDCP formatted string.
        """
        out = StringIO()
        writer = PCDCPWriter()
        writer.write(out, timeseries, channels)
        return out.getvalue()
