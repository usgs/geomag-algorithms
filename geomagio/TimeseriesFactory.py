"""Abstract Timeseries Factory Interface."""
import numpy.ma as ma
import obspy

class TimeseriesFactory(object):
    """Base class for timeseries factories.

    Attributes
    ----------
    observatory : str
        default observatory code, usually 3 characters.
    channels : array_like
        default list of channels to load, optional.
        default ('H', 'D', 'Z', 'F')
    type : {'definitive', 'provisional', 'quasi-definitive', 'variation'}
        default data type, optional.
        default 'variation'.
    interval : {'daily', 'hourly', 'minute', 'monthly', 'second'}
        data interval, optional.
        default 'minute'.
    """
    def __init__(self, observatory=None, channels=('H', 'D', 'Z', 'F'),
            type='variation', interval='minute'):
        self.observatory = observatory
        self.channels = channels
        self.type = type
        self.interval = interval

    def get_timeseries(self, starttime, endtime, observatory=None,
            channels=None, type=None, interval=None):
        """Get timeseries data.

        Support for specific channels, types, and intervals varies
        between factory and observatory.  Subclasses should raise
        TimeseriesFactoryException if the data is not available, or
        if an error occurs accessing data.

        Parameters
        ----------
        starttime : UTCDateTime
            time of first sample in timeseries.
        endtime : UTCDateTime
            time of last sample in timeseries.
        observatory : str
            observatory code, usually 3 characters, optional.
            uses default if unspecified.
        channels : array_like
            list of channels to load, optional.
            uses default if unspecified.
        type : {'definitive', 'provisional', 'quasi-definitive', 'variation'}
            data type, optional.
            uses default if unspecified.
        interval : {'daily', 'hourly', 'minute', 'monthly', 'second'}
            data interval, optional.
            uses default if unspecified.

        Returns
        -------
        obspy.core.Stream
            stream containing traces for requested timeseries.

        Raises
        ------
        TimeseriesFactoryException
            if any parameters are unsupported, or errors occur loading data.
        """
        raise NotImplementedError('"get_timeseries" not implemented')

    def put_timeseries(self, timeseries, starttime=None, endtime=None,
            channels=None, type=None, interval=None):
        """Store timeseries data.

        Parameters
        ----------
        timeseries : obspy.core.Stream
            stream containing traces to store.
        starttime : UTCDateTime
            time of first sample in timeseries to store.
            uses first sample if unspecified.
        endtime : UTCDateTime
            time of last sample in timeseries to store.
            uses last sample if unspecified.
        channels : array_like
            list of channels to store, optional.
            uses default if unspecified.
        type : {'definitive', 'provisional', 'quasi-definitive', 'variation'}
            data type, optional.
            uses default if unspecified.
        interval : {'daily', 'hourly', 'minute', 'monthly', 'second'}
            data interval, optional.
            uses default if unspecified.
        Raises
        ------
        TimeseriesFactoryException
            if any errors occur.
        """
        raise NotImplementedError('"put_timeseries" not implemented')

    def create_gap_stream(self, timeseries, channels):
        gap_stream = obspy.core.Stream()
        for channel in channels:
            for trace in timeseries.select(channel=channel):
                trace.data = ma.masked_invalid(trace.data)
                for data in trace.split():
                    gap_stream += data

        # gaps are returned from getGaps from the point before, to the
        # point after, so remove that point to get the gap.
        gaps = gap_stream.getGaps()
        for gap in gaps:
            gap[4] = gap[4] + 60
            gap[5] = gap[5] - 60

        # sync gaps across channels

        full_gaps = []
        gap_cnt = len(gaps)
        for i in range(0, gap_cnt):
            gap = gaps[i]
            if self._contained_in_gap(gap, full_gaps):
                continue

            starttime = gap[4]
            endtime = gap[5]
            for x in range(i+1, gap_cnt):
                nxtgap = gaps[x]
                if ((nxtgap[4] >= starttime and nxtgap[4] <= endtime)
                        or (nxtgap[5] >= starttime and nxtgap[5] <= endtime)):
                    if nxtgap[4] < starttime:
                        starttime = nxtgap[4]
                    if nxtgap[5] > endtime:
                        endtime = nxtgap[5]

            full_gaps.append([starttime, endtime])

        return (full_gaps, gaps)

    def _contained_in_gap(self, gap, gaps):
        starttime = gap[4]
        endtime = gap[5]
        for gap in gaps:
            if starttime >= gap[0] and endtime <= gap[1]:
                    return True
        return False
