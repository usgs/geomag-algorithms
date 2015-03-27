"""Factory that loads IAGA2002 Files."""

from IAGA2002Factory import IAGA2002Factory

# pattern for iaga 2002 file names


class StreamIAGA2002Factory(IAGA2002Factory):
    def __init__(self, stream, observatory=None, channels=None,
            type=None, interval=None):
        IAGA2002Factory.__init__(self, None, observatory, channels,
            type, interval)
        self._stream = stream

    def get_timeseries(self, starttime, endtime, observatory=None,
            channels=None, type=None, interval=None):
        return IAGA2002Factory.parse_string(self, self._stream)

    def put_timeseries(self, timeseries, starttime=None, endtime=None,
            channels=None, type=None, interval=None):
        IAGA2002Factory.write_file(self, self._stream, timeseries, channels)
