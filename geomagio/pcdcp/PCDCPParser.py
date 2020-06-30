"""Parsing methods for the PCDCP Format."""


import numpy

# values that represent missing data points in PCDCP
NINES = numpy.int("9999999")
NINES_RAW = numpy.int("99999990")
NINES_DEG = numpy.int("9999")


class PCDCPParser(object):
    """PCDCP parser.

    Attributes
    ----------
    header : dict
        parsed PCDCP header.
    channels : array
        parsed channel names.
    times : array
        parsed timeseries times.
    data : dict
        keys are channel names (order listed in ``self.channels``).
        values are ``numpy.array`` of timeseries values, array values are
        ``numpy.nan`` when values are missing.
    """

    def __init__(self):
        """Create a new PCDCP parser."""
        # header fields
        self.header_fields = [
            "station",
            "year",
            "yearday",
            "date",
            "orientation",
            "resolution",
            "Version",
        ]
        self.header = {}
        # resolution (float)
        self.resolution = 0.0
        # array of channel names
        self.channels = []
        # timestamps of data (datetime.datetime)
        self.times = []
        # dictionary of data (channel : numpy.array<float64>)
        self.data = {}
        # temporary storage for data being parsed
        self._parsedata = None

    def parse(self, data):
        """Parse a string containing PCDCP formatted data.

        Parameters
        ----------
        data : str
            PCDCP formatted file contents.
        """
        self._set_channels()

        parsing_header = True
        lines = data.splitlines()
        for line in lines:
            if parsing_header:
                self._parse_header(line)
                parsing_header = False
            else:
                self._parse_data(line)
        self._post_process()

    def _parse_header(self, line):
        """Parse header line.

        Adds value to ``self.header``.
        """
        self.header = dict(
            zip(self.header_fields, line.split(None, len(self.header_fields)))
        )

        if "nT" in self.header["resolution"]:
            self.resolution = float(self.header["resolution"].split("nT")[0])
        else:
            self.resolution = float(self.header["resolution"].split("*")[1])

        return

    def _parse_data(self, line):
        """Parse one data point in the timeseries.

        Adds time to ``self.times``.
        Adds channel values to ``self.data``.
        """
        values = line.split()
        for (value, column) in zip(values, self._parsedata):
            column.append(value)

    def _post_process(self):
        """Post processing after data is parsed.

        Converts data to numpy arrays.
        Replaces empty values with ``numpy.nan``.
        """
        self.times = self._parsedata[0]

        for channel, data in zip(self.channels, self._parsedata[1:]):
            data = numpy.array(data, dtype=numpy.float64)
            # filter empty values
            data[data == NINES] = numpy.nan
            data[data == NINES_RAW] = numpy.nan
            data = numpy.multiply(data, self.resolution)
            self.data[channel] = data

        self._parsedata = None

    def _set_channels(self):
        """Adds channel names to ``self.channels``.
        Creates empty values arrays in ``self.data``.
        """
        self.channels.append("H")
        self.channels.append("E")
        self.channels.append("Z")
        self.channels.append("F")

        self._parsedata = ([], [], [], [], [])
