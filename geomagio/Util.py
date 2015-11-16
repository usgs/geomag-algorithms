import urllib2
import numpy
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
