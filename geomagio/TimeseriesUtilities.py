"""Timeseries Utilities"""
import numpy.ma as ma
import obspy
import numpy

def get_timeseries_gaps(timeseries, channels, starttime, endtime):
    gaps = {}
    for channel in channels:
        stream_gap = get_stream_gaps(
                timeseries.select(channel=channel), starttime, endtime)
        gaps[channel] = stream_gap

    return gaps


def get_stream_gaps(stream, starttime, endtime):
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
    all_gaps = []
    gap_stream = []
    for channel in channels:
        gap_stream.extend(gaps[channel])

    if len(gap_stream) == 0:
        return []

    sorted_gaps = sorted(gap_stream, key=lambda starttime: starttime[1])
    merged_gaps = []

    gap = sorted_gaps[0]
    for i in range(1,len(sorted_gaps)):
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
    for output_gap in output_gaps:
        for input_gap in input_gaps:
            if (output_gap[0] >= input_gap[0] and
                    output_gap[0] <= input_gap[1] and
                    output_gap[1] <= input_gap[1]):
                return False
    return True

def get_seconds_of_interval(interval):
    if interval == 'second':
        return 1
    if interval == 'minute':
        return 60
    if interval == 'hourly':
        return 3600
    if interval == 'daily':
        return 86400
