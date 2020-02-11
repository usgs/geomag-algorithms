import numpy
import os
from obspy.core import Stats, Trace
from io import BytesIO


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
        when <= 0, returns one interval from start to end.
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
    if size <= 0:
        return [{
            'start': starttime,
            'end': endtime
        }]
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


def read_file(filepath):
    """Open and read file contents.

    Parameters
    ----------
    filepath : str
        path to a file

    Returns
    -------
    str
        contents of file

    Raises
    ------
    IOError
        if file does not exist
    """
    file_data = None
    with open(filepath, 'r') as f:
        file_data = f.read()
    return file_data


def read_url(url, connect_timeout=15, max_redirects=5, timeout=300):
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
    IOError
        if any occurs
    """
    try:
        # short circuit file urls
        filepath = get_file_from_url(url)
        return read_file(filepath)
    except IOError as e:
        raise e
    except Exception:
        pass
    # wait to import pycurl until it is needed
    import pycurl
    content = None
    out = BytesIO()
    curl = pycurl.Curl()
    try:
        curl.setopt(pycurl.FOLLOWLOCATION, 1)
        curl.setopt(pycurl.MAXREDIRS, max_redirects)
        curl.setopt(pycurl.CONNECTTIMEOUT, connect_timeout)
        curl.setopt(pycurl.TIMEOUT, timeout)
        curl.setopt(pycurl.NOSIGNAL, 1)
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEFUNCTION, out.write)
        curl.perform()
        content = out.getvalue()
        content = content.decode('utf-8')
    except pycurl.error as e:
        raise IOError(e.args)
    finally:
        curl.close()
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
