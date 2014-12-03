import numpy
from obspy.core.utcdatetime import UTCDateTime
from TimeseriesException import TimeseriesException


class Timeseries(object):
    """A sequence of samples at regular intervals.

    Attributes
    ----------
    observatory : string
        the observatory code
    channels : dict
        keys are channel names.
        values are numpy arrays of timeseries values.
        numpy.nan is used in arrays when values are missing.
    starttime : UTCDateTime
        time of the first sample.
    endtime : UTCDateTime
        time of the last sample.
    metadata : array_like
        array of metadata dict objects describing the timeseries.
        metadata keys and values vary by factory.
        when multiple metadata exist, starttime and endtime keys
        describe metadata extents.
    length : int
        number of samples in each channel.
    rate : float
        sample rate in hertz.
    """
    def __init__(self, observatory, channels, starttime, endtime,
            metadata=None):
        self.observatory = observatory
        self.channels = channels
        self.starttime = starttime
        self.endtime = endtime
        self.metadata = metadata or []
        self.length = len(channels[channels.keys()[0]])
        self.rate = (self.length - 1) / (endtime - starttime)

    def get_time(self, i):
        """Get the time of a sample for the given index.

        Parameters
        ----------
        i : int
            index of the sample

        Returns
        -------
        UTCDateTime
            time of the i-th sample
        """
        return UTCDateTime(self.starttime.timestamp + (i / self.rate))

    def get_index(self, time, exact=True):
        """Get the index of the sample for a given time.

        Parameters
        ----------
        time : UTCDateTime
            the given time.
        exact : Boolean, optional
            when True, return None if no sample exists at exactly ``time``.
            when False, return time of nearest sample.

        Returns
        -------
        int
            index of sample for given time, or None.
        """
        index = round((time - self.starttime) * self.rate)
        if exact:
            indexTime = self.get_time(index)
            if indexTime != time:
                return None
        return index

    def __add__(self, other):
        """Combine two timeseries objects.

        Parameters
        ----------
        other : Timeseries
            timeseries object to append to current object.
            other must have the same observatory, same sampling rate,
                same channels, and result in a continuous timeseries
                (i.e. ``self.endtime + 1/rate == other.starttime``).

        Returns
        -------
        Timeseries
            new object with all samples of self and other.

        Raises
        ------
        TimeseriesException
            if the preconditions for ``other`` are not met.
        """
        if self.observatory != other.observatory:
            raise TimeseriesException('cannot add, different observatory')
        if self.rate != other.rate:
            raise TimeseriesException('cannot add, different rates')
        if sorted(self.channels.keys()) != sorted(other.channels.keys()):
            raise TimeseriesException('cannot add, different channels')
        expected_start = self.get_time(self.length)
        if expected_start != other.starttime:
            print 'expected=', expected_start, 'start=', other.starttime
            raise TimeseriesException('cannot add, non continuous timeseries')
        merged_channels = {}
        for key in self.channels.keys():
            merged_channels[key] = numpy.concatenate(
                    (self.channels[key], other.channels[key]))
        return Timeseries(self.observatory, merged_channels,
                self.starttime, other.endtime, self.metadata + other.metadata)

    def __len__(self):
        """Get the number of samples in each channel.

        Returns
        -------
        int
            the number of samples in each channel.
        """
        return self.length

    def __str__(self):
        """Get a summary of this timeseries.

        Returns
        -------
        str
            summary of this timeseries
        """
        return 'Timeseries ' + str(self.observatory) + \
                ' ' + str(self.channels.keys()) + \
                ' ' + str(self.length) + ' samples' + \
                ' at ' + str(self.rate) + ' hertz' + \
                ' (' +str(self.starttime) + ' - ' + str(self.endtime) + ')'
