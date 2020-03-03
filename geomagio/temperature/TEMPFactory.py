"""Factory that loads temp/volt Files."""
from __future__ import absolute_import

from ..TimeseriesFactory import TimeseriesFactory
from .TEMPWriter import TEMPWriter


# pattern for temp file names
TEMP_FILE_PATTERN = "%(obs)s%(y)s%(j)s.%(i)s"


class TEMPFactory(TimeseriesFactory):
    """TimeseriesFactory for temp/volt formatted files.

    Parameters
    ----------
    urlTemplate : str
        A string that contains any of the following replacement patterns:
        - '%(i)s' : interval abbreviation
        - '%(interval)s' interval name
        - '%(julian)s' julian day formatted as JJJ
        - '%(obs)s' lowercase observatory code
        - '%(OBS)s' uppercase observatory code
        - '%(t)s' type abbreviation
        - '%(type)s' type name
        - '%(year)s' year formatted as YYYY
        - '%(ymd)s' time formatted as YYYYMMDD
    """

    def __init__(self, **kwargs):
        TimeseriesFactory.__init__(self, **kwargs)

    def write_file(self, fh, timeseries, channels):
        """writes timeseries data to the given file object.

        Parameters
        ----------
        fh: file object
        timeseries : obspy.core.Stream
            stream containing traces to store.
        channels : array_like
            list of channels to store
        """
        TEMPWriter().write(fh, timeseries, channels)
