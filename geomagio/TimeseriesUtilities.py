"""Timeseries Utilities"""
import numpy


def get_timeseries_gaps(timeseries, channels, starttime, endtime):
    """Get gaps in a given timeseries
    Parameters
    ----------
    timeseries: obspy.core.stream
        the stream to check for gaps in
    channels: array_like
        list of channels to look for gaps in
    starttime: obspy.core.UTCDateTime
        time of first sample.
    endtime: obspy.core.UTCDateTime
        time of last sample.

    Returns
    -------
    dictionary of channel gaps arrays

    Notes
    -----
    Returns a dictionary with channel: gaps array pairs. Where the gaps array
        consists of arrays of starttime/endtime pairs representing each gap.
    """
    gaps = {}
    for channel in channels:
        stream_gap = get_stream_gaps(
                timeseries.select(channel=channel), starttime, endtime)
        gaps[channel] = stream_gap

    return gaps


def get_stream_gaps(stream, starttime, endtime):
    """Gets gaps in a stream representing a single channel
    Parameters
    ----------
    stream: obspy.core.stream
        a stream containing a single channel of data.
    starttime: obspy.core.UTCDateTime
        time of first sample.
    endtime: obspy.core.UTCDateTime
        time of last sample.

    Returns
    -------
    array of gaps
    """
    gaps = []
    gap = None

    i = 0
    data = stream[0].data
    length = len(data)
    for i in xrange(0, length):
        if numpy.isnan(data[i]) and gap is None:
            gap = [starttime + i * 60]
        if not numpy.isnan(data[i]) and gap is not None:
            gap.append(starttime + (i - 1) * 60)
            gaps.append(gap)
            gap = None
    if gap is not None:
        gap.append(endtime)
        gaps.append(gap)

    return gaps


def get_merged_gaps(gaps, channels):
    """Get gaps merged across channels/streams
    Parameters
    ----------
    gaps: dictionary
        contains channel/gap array pairs
    channels: array_like
        array of channels to look for gaps in

    Returns
    -------
    array_like
        an array of startime/endtime arrays representing gaps.

    Notes
    -----
    Takes an dictionary of gaps, and merges those gaps across channels,
        returning an array of the merged gaps.
    """
    gap_stream = []
    for channel in channels:
        gap_stream.extend(gaps[channel])

    if len(gap_stream) == 0:
        return []

    sorted_gaps = sorted(gap_stream, key=lambda starttime: starttime[1])
    merged_gaps = []

    gap = sorted_gaps[0]
    for i in range(1, len(sorted_gaps)):
        nxtgap = sorted_gaps[i]
        if nxtgap[0] >= gap[0] and nxtgap[0] <= gap[1]:
            if nxtgap[1] > gap[1]:
                gap[1] = nxtgap[1]
        else:
            merged_gaps.append(gap)
            gap = nxtgap
    merged_gaps.append(gap)

    return merged_gaps


def is_new_data(input_gaps, output_gaps):
    """Is new data available in gaps
    Parameters
    ----------
    input_gaps: array_like
        an array of startime/endtime gap pairs holding the input gaps
    output_gaps: array_like
        an array of starttime/endtime gap pairs holding the ouput gaps

    Returns
    boolean
        True if there's new data available, False otherwise
    """
    for output_gap in output_gaps:
        for input_gap in input_gaps:
            if (output_gap[0] >= input_gap[0] and
                    output_gap[0] <= input_gap[1] and
                    output_gap[1] <= input_gap[1]):
                return False
    return True


def gap_is_new_data(input_gaps, output_gap):
    """Is new data available for a single gap
    Parameters
    ----------
    input_gaps: array_like
        an array of startime/endtime gap pairs holding the input gaps
    output_gaps: array_like
        starttime/endtime pair representing a single gap

    Returns
    boolean
        True if there's new data available for the gap, False otherwise
    """
    for input_gap in input_gaps:
        if (output_gap[0] >= input_gap[0] and
                output_gap[0] <= input_gap[1] and
                output_gap[1] <= input_gap[1]):
            return False
    return True


def get_seconds_of_interval(interval):
    """Gets number of seconds for a given interval string
    Parameters
    ----------
    interval: string
        The string representing an interval size
    """
    if interval == 'second':
        return 1
    if interval == 'minute':
        return 60
    if interval == 'hourly':
        return 3600
    if interval == 'daily':
        return 86400
