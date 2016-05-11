import urllib2
import numpy
import os
from obspy.core import Stats, Trace


class ObjectView(object):
    """
    Wrap a dictionary so its properties can be accessed as an object.

    Parameters
    ----------
    d : dictionary
        The dictionary to wrap.
    """
    def __init__(self, d):
        self.__dict__ = d

    def __str__(self):
        """
        Override string representation to output wrapped dictionary.
        """
        return str(self.__dict__)


def get_file_from_url(url, createParentDirectory=False):
    """Get a file for writing.

    Ensures parent directory exists.

    Parameters
    ----------
    url : str
        path to file
    createParentDirectory : bool
        whether to create parent directory if it does not exist.
        useful when preparing to write to the returned file.

    Returns
    -------
    str
        path to file without file:// prefix

    Raises
    ------
    Exception
        if url does not start with file://
    """
    if not url.startswith('file://'):
        raise Exception('Only file urls are supported by get_file_from_url')
    filename = url.replace('file://', '')
    if createParentDirectory:
        parent = os.path.dirname(filename)
        if not os.path.exists(parent):
            os.makedirs(parent)
    return filename


def get_intervals(starttime, endtime, size=86400, align=True, trim=False):
    """Divide an interval into smaller intervals.

    Divides the interval [starttime, endtime] into chunks.

    Parameters
    ----------
    starttime : obspy.core.UTCDateTime
        start of time interval to divide
    endtime : obspy.core.UTCDateTime
        end of time interval to divide
    size : int
        size of each interval in seconds.
    align : bool
        align intervals to unix epoch.
        (works best when size evenly divides a day)
    trim : bool
        whether to trim first/last interval to starttime and endtime.

    Returns
    -------
    list<dict>
        each dictionary has the keys "starttime" and "endtime"
        which represent [intervalstart, intervalend).
    """
    if align:
        # align based on size
        time = starttime - (starttime.timestamp % size)
    else:
        time = starttime
    intervals = []
    while time < endtime:
        start = time
        time = time + size
        end = time
        if trim:
            if start < starttime:
                start = starttime
            if end > endtime:
                end = endtime
        intervals.append({
            'start': start,
            'end': end
        })
    return intervals


def read_url(url):
    """Open and read url contents.

    Parameters
    ----------
    url : str
        A urllib2 compatible url, such as http:// or file://.

    Returns
    -------
    str
        contents returned by url.

    Raises
    ------
    urllib2.URLError
        if any occurs
    """
    response = urllib2.urlopen(url)
    content = None
    try:
        content = response.read()
    except urllib2.URLError, e:
        print e.reason
        raise
    finally:
        response.close()
    return content


def create_empty_trace(trace, channel):
    """
    Utility to create an empty trace, similar to another trace.

    Parameters
    ----------
    trace: obspy.core.Trace
        Trace that is source of most metadata, including array length.
    channel: String
        Channel name for created Trace.

    Returns
    -------
    obspy.core.Trace
        a Trace object, filled with numpy.nan.
    """
    stats = Stats(trace.stats)
    stats.channel = channel
    count = len(trace.data)
    numpy_data = numpy.full((count), numpy.nan)
    return Trace(numpy_data, stats)
