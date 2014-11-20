"""
Parsing methods for the IAGA2002 Format.
"""


from obspy.core.utcdatetime import UTCDateTime
import numpy


# values that represent missing data points in IAGA2002
EIGHTS = numpy.float64('88888.88')
NINES = numpy.float64('99999.99')


def merge_comments(comments):
    """
    Combine multi-line, period-delimited comments.
    """
    merged = []
    partial = None
    for comment in comments:
        if partial is None:
            partial = comment
        else:
            partial = partial + ' ' + comment
        # comments end with period
        if partial.endswith('.'):
            merged.append(partial)
            partial = None
    # comment that doesn't end in a period
    if partial is not None:
        merged.append(partial)
    return merged


class Parser(object):
    """
    IAGA2002 parser.
    """

    def __init__(self):
        """
        Create a new IAGA2002 parser.
        """
        # header fields
        self.headers = {}
        # header comments
        self.comments = []
        # array of channel names
        self.channels = []
        # timestamps of data (obspy.core.utcdatetime.UTCDateTime)
        self.times = []
        # dictionary of data (channel : numpy.array<float64>)
        self.data = {}

    def parse(self, data):
        """
        Parse a string containing IAGA2002 formatted data.
        """
        parsing_headers = True
        lines = data.splitlines()
        for line in lines:
            if parsing_headers:
                if line.startswith(' ') and line.endswith('|'):
                    # still in headers
                    if line.startswith(' #'):
                        self._parse_comment(line)
                    else:
                        self._parse_header(line)
                else:
                    parsing_headers = False
                    self._parse_channels(line)
            else:
                self._parse_data(line)
        self._post_process()
        return self

    def _parse_header(self, line):
        """
        Parse a header line.
        """
        key = line[1:24].strip()
        value = line[24:69].strip()
        self.headers[key] = value

    def _parse_comment(self, line):
        """
        Parse a header comment line.
        """
        self.comments.append(line[2:69].strip())

    def _parse_channels(self, line):
        """
        Parse the data header that contains channel names.
        """
        iaga_code = self.headers['IAGA CODE']
        self.channels.append(line[30:40].strip().replace(iaga_code, ''))
        self.channels.append(line[40:50].strip().replace(iaga_code, ''))
        self.channels.append(line[50:60].strip().replace(iaga_code, ''))
        self.channels.append(line[60:69].strip().replace(iaga_code, ''))
        # create data arrays
        for channel in self.channels:
            self.data[channel] = []

    def _parse_data(self, line):
        """
        Parse one data point in the timeseries
        """
        channels = self.channels
        self.times.append(UTCDateTime(line[0:24]))
        self.data[channels[0]].append(line[31:40].strip())
        self.data[channels[1]].append(line[41:50].strip())
        self.data[channels[2]].append(line[51:60].strip())
        self.data[channels[3]].append(line[61:70].strip())

    def _post_process(self):
        """
        Post processing after data is parsed.
        """
        self.comments = merge_comments(self.comments)
        self.parse_comments()
        for channel in self.data:
            data = numpy.array(self.data[channel], dtype=numpy.float64)
            # filter empty values
            data[data == EIGHTS] = numpy.nan
            data[data == NINES] = numpy.nan
            self.data[channel] = data

    def parse_comments(self):
        """
        Parse header values embedded in comments.
        """
        for comment in self.comments:
            if comment.startswith('DECBAS'):
                # parse DECBAS
                decbas = comment.replace('DECBAS', '').strip()
                self.headers['DECBAS'] = decbas[:decbas.find(' ')]


def main(data):
    """
    Parse and print an IAGA2002 string.
    """
    from pprint import pprint
    pprint(Parser().parse(data))


if __name__ == '__main__':
    import sys
    main(sys.stdin.read())
