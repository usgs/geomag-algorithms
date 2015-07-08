"""Timeseries Utilities"""
import numpy


def get_stream_gaps(stream):
    """Get gaps in a given stream
    Parameters
    ----------
    stream: obspy.core.Stream
        the stream to check for gaps
    channels: array_like
        list of channels to check for gaps

    Returns
    -------
    dictionary of channel gaps arrays

    Notes
    -----
    Returns a dictionary with channel: gaps array pairs. Where the gaps array
        consists of arrays of starttime/endtime pairs representing each gap.
    """
    gaps = {}
    for trace in stream:
        channel = trace.stats.channel
        gaps[channel] = get_trace_gaps(trace)
    return gaps


def get_trace_gaps(trace):
    """Gets gaps in a trace representing a single channel
    Parameters
    ----------
    trace: obspy.core.Trace
        a stream containing a single channel of data.

    Returns
    -------
    array of gaps, which is empty when there are no gaps.
    each gap is an array [start of gap, end of gap, next sample]
    """
    gaps = []
    gap = None
    data = trace.data
    stats = trace.stats
    starttime = stats.starttime
    length = len(data)
    delta = stats.delta
    for i in xrange(0, length):
        if numpy.isnan(data[i]):
            if gap is None:
                # start of a gap
                gap = [starttime + i * delta]
        else:
            if gap is not None:
                # end of a gap
                gap.extend([
                        starttime + (i - 1) * delta,
                        starttime + i * delta])
                gaps.append(gap)
                gap = None
    # check for gap at end
    if gap is not None:
        gap.extend([
                starttime + (length - 1) * delta,
                starttime + length * delta])
        gaps.append(gap)
    return gaps


def get_merged_gaps(gaps):
    """Get gaps merged across channels/streams
    Parameters
    ----------
    gaps: dictionary
        contains channel/gap array pairs

    Returns
    -------
    array_like
        an array of startime/endtime arrays representing gaps.

    Notes
    -----
    Takes an dictionary of gaps, and merges those gaps across channels,
        returning an array of the merged gaps.
    """
    merged_gaps = []
    for key in gaps:
        merged_gaps.extend(gaps[key])
    # sort gaps so earlier gaps are before later gaps
    sorted_gaps = sorted(merged_gaps, key=lambda gap: gap[0])
    # merge gaps that overlap
    merged_gaps = []
    merged_gap = None
    for gap in sorted_gaps:
        if merged_gap is None:
            # start of gap
            merged_gap = gap
        elif gap[0] > merged_gap[2]:
            # next gap starts after current gap ends
            merged_gaps.append(merged_gap)
            merged_gap = gap
        elif gap[0] <= merged_gap[2]:
            # next gap starts at or before next data
            if gap[1] > merged_gap[1]:
                # next gap ends after current gap ends, extend current
                merged_gap[1] = gap[1]
                merged_gap[2] = gap[2]
    if merged_gap is not None:
        merged_gaps.append(merged_gap)
    return merged_gaps
