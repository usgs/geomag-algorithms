"""Factory for json files."""
from __future__ import absolute_import

import obspy.core
from .. import ChannelConverter
from ..TimeseriesFactory import TimeseriesFactory
from .JSONWriter import JSONWriter


class JSONFactory(TimeseriesFactory):
    """TimeseriesFactory for IAGA 2002 formatted files.

    Parameters
    ----------
    urlTemplate : str
        A string that contains any of the following replacement patterns:
        - '%(i)s' : interval abbreviation
        - '%(interval)s' interval name
        - '%(obs)s' lowercase observatory code
        - '%(OBS)s' uppercase observatory code
        - '%(t)s' type abbreviation
        - '%(type)s' type name
        - '%(ymd)s' time formatted as YYYYMMDD
    """

    def __init__(self, **kwargs):
        TimeseriesFactory.__init__(self, **kwargs)

    # TODO: Write parser method
    def parse_string(self, data, observatory=None, interval='minute',
            **kwargs):
        """Parse the contents of a string in the format of an json file.

        Parameters
        ----------
        jsonString : str
            string containing IAGA2002 content.
        observatory : str
            observatory in case headers are unavailable.
            parses observatory from headers when available.
        Returns
        -------
        obspy.core.Stream
            parsed data.
        """
        pass

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
        JSONWriter().write(fh, timeseries, channels)
