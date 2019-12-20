"""Factory that loads IMFV122 Files."""
from __future__ import absolute_import

import obspy.core
from .. import ChannelConverter
from ..TimeseriesFactory import TimeseriesFactory
from .IMFV122Parser import IMFV122Parser


class IMFV122Factory(TimeseriesFactory):
    """TimeseriesFactory for IMFV122 formatted files.

    Parameters
    ----------
    See TimeseriesFactory

    See Also
    --------
    IMFV122Parser
    """

    def __init__(self, **kwargs):
        TimeseriesFactory.__init__(self, **kwargs)

    def parse_string(self, data, observatory=None, **kwargs):
        """Parse the contents of a string in the format of an IAGA2002 file.

        Parameters
        ----------
        iaga2002String : str
            string containing IAGA2002 content.
        observatory : str
            observatory in case headers are unavailable.
            parses observatory from headers when available.
        Returns
        -------
        obspy.core.Stream
            parsed data.
        """
        parser = IMFV122Parser(observatory=observatory)
        parser.parse(data)
        metadata = parser.metadata
        starttime = obspy.core.UTCDateTime(parser.times[0])
        endtime = obspy.core.UTCDateTime(parser.times[-1])
        data = parser.data
        length = len(data[list(data.keys())[0]])
        rate = (length - 1) / (endtime - starttime)
        stream = obspy.core.Stream()
        for channel in list(data.keys()):
            stats = obspy.core.Stats(metadata)
            stats.starttime = starttime
            stats.sampling_rate = rate
            stats.npts = length
            stats.channel = channel
            if channel == 'D':
                data[channel] = ChannelConverter.get_radians_from_minutes(
                    data[channel])
            stream += obspy.core.Trace(data[channel], stats)
        return stream
