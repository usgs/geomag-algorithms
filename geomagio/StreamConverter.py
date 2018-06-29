"""Convert streams from one coordinate system to another.

We use three coordinate systems.
Geo: Based on Geographic North.  X, Y, Z, F
     X is north, Y is east, Z is down
Obs: Based on the observatories orientaion. H, E, Z, F, d0
Mag: Based on Magnetic North. H, D, Z, F
"""
from __future__ import absolute_import

import numpy
import obspy.core
from . import ChannelConverter


def get_geo_from_mag(mag):
    """Convert a stream to geographic coordinate system.

    Parameters
    ----------
    stream : obspy.core.Stream
        stream containing observatory components H, D, Z, and F.

    Returns
    -------
    obspy.core.Stream
        new stream object containing geographic components X, Y, Z, and F.
    """
    h = mag.select(channel='H')[0]
    d = mag.select(channel='D')[0]
    z = mag.select(channel='Z')
    f = mag.select(channel='F')
    mag_h = h.data
    mag_d = d.data
    (geo_x, geo_y) = ChannelConverter.get_geo_from_mag(mag_h, mag_d)
    return obspy.core.Stream((
        __get_trace('X', h.stats, geo_x),
        __get_trace('Y', d.stats, geo_y),
        )) + z + f


def get_geo_from_obs(obs):
    """Convert a stream to geographic coordinate system.

    Parameters
    ----------
    stream : obspy.core.Stream
        stream containing observatory components H, D or E, Z, and F.

    Returns
    -------
    obspy.core.Stream
        new stream object containing geographic components X, Y, Z, and F.
    """
    return get_geo_from_mag(get_mag_from_obs(obs))


def get_deltaf_from_geo(geo):
    """Get deltaf given geographic coordinate values

    Parameters
    ----------
    obs: obspy.core.Stream
        stream containing the observatory components H, D or E, Z, and F.

    Returns
    -------
    obspy.core.Stream
        stream object containing delta f values
    """
    x = geo.select(channel='X')[0]
    y = geo.select(channel='Y')[0]
    z = geo.select(channel='Z')[0]
    fs = geo.select(channel='F')[0]
    fv = ChannelConverter.get_computed_f_using_squares(x, y, z)
    G = ChannelConverter.get_deltaf(fv, fs)
    return obspy.core.Stream((
            __get_trace('G', x.stats, G), ))


def get_deltaf_from_obs(obs):
    """Get deltaf given observatory coordinate values

    Parameters
    ----------
    obs: obspy.core.Stream
        stream containing the observatory components H, D or E, Z, and F.

    Returns
    -------
    obspy.core.Stream
        stream object containing delta f values
    """
    h = obs.select(channel='H')[0]
    z = obs.select(channel='Z')[0]
    fs = obs.select(channel='F')[0]
    e = __get_obs_e_from_obs(obs)
    fv = ChannelConverter.get_computed_f_using_squares(h, e, z)
    G = ChannelConverter.get_deltaf(fv, fs)
    return obspy.core.Stream((
            __get_trace('G', h.stats, G), ))


def get_mag_from_geo(geo):
    """Convert a stream to magnetic coordinate system.

    Parameters
    ----------
    geo: obspy.core.Stream
        stream containing observatory components X, Y, Z, and F.

    Returns
    -------
    obspy.core.Stream
        new stream object containing magnetic components H, D, Z, and F.
    """
    x = geo.select(channel='X')[0]
    y = geo.select(channel='Y')[0]
    z = geo.select(channel='Z')
    f = geo.select(channel='F')
    geo_x = x.data
    geo_y = y.data
    (mag_h, mag_d) = ChannelConverter.get_mag_from_geo(geo_x, geo_y)
    return obspy.core.Stream((
            __get_trace('H', x.stats, mag_h),
            __get_trace('D', y.stats, mag_d),
            )) + z + f


def get_mag_from_obs(obs):
    """Convert a stream to magnetic coordinate system.

    Parameters
    ----------
    obs : obspy.core.Stream
        stream containing observatory components H, D or E, Z, and F.

    Returns
    -------
    obspy.core.Stream
        new stream object containing magnetic components H, D, Z, and F.
    """
    h = obs.select(channel='H')[0]
    e = __get_obs_e_from_obs(obs)
    z = obs.select(channel='Z')
    f = obs.select(channel='F')
    obs_h = h.data
    obs_e = e.data
    d0 = ChannelConverter.get_radians_from_minutes(
            numpy.float64(e.stats.declination_base) / 10)
    (mag_h, mag_d) = ChannelConverter.get_mag_from_obs(obs_h, obs_e, d0)
    return obspy.core.Stream((
            __get_trace('H', h.stats, mag_h),
            __get_trace('D', e.stats, mag_d),
            )) + z + f


def get_obs_from_geo(geo, include_d=False):
    """Convert a stream to observatory coordinate system.

    Parameters
    ----------
    stream : obspy.core.Stream
        stream containing geographic components X, Y, Z, and F.
    include_d : boolean
        whether to also include the observatory D component.

    Returns
    -------
    obspy.core.Stream
        new stream object containing observatory components H, D, E, Z, and F.
    """
    return get_obs_from_mag(get_mag_from_geo(geo), include_d)


def get_obs_from_mag(mag, include_d=False):
    """Convert a stream to magnetic observatory coordinate system.

    Parameters
    ----------
    stream: obspy.core.Stream
        stream containing magnetic components H, D, Z, and F.
    include_d: boolean
        whether to also include the observatory D component
    Returns
    -------
    obspy.core.Stream
        new stream object containing observatory components H, D, E, Z, and F
    """
    h = mag.select(channel='H')[0]
    d = mag.select(channel='D')[0]
    z = mag.select(channel='Z')
    f = mag.select(channel='F')

    mag_h = h.data
    mag_d = d.data
    d0 = ChannelConverter.get_radians_from_minutes(
        numpy.float64(d.stats.declination_base) / 10)
    (obs_h, obs_e) = ChannelConverter.get_obs_from_mag(mag_h, mag_d, d0)

    traces = (
        __get_trace('H', h.stats, obs_h),
        __get_trace('E', d.stats, obs_e),
        )
    if include_d:
        obs_d = ChannelConverter.get_obs_d_from_obs(obs_h, obs_e)
        traces = traces + (__get_trace('D', d.stats, obs_d),)
    return obspy.core.Stream(traces) + z + f


def get_obs_from_obs(obs, include_e=False, include_d=False):
    """Fill in the observatory parameters as requested

    Parameters
    ----------
    stream: obspy.core.Stream
        stream containing the observatory components H, D or E, Z, and F.
    include_e: boolean
        whether to include the e component
    include_d: boolean
        whether to include the d component

    Returns
    -------
    obspy.core.Stream
        new stream object containing observatory components H, D, E, Z, and F
    """
    h = obs.select(channel='H')[0]
    z = obs.select(channel='Z')
    f = obs.select(channel='F')
    traces = (h, )
    if include_d:
        d = __get_obs_d_from_obs(obs)
        traces = traces + (d, )
    if include_e:
        e = __get_obs_e_from_obs(obs)
        traces = traces + (e, )
    return obspy.core.Stream(traces) + z + f


def __get_trace(channel, stats, data):
    """Utility to create a new trace object.

    Parameters
    ----------
    channel : str
        channel name.
    stats : obspy.core.Stats
        channel metadata to clone.
    data : numpy.array
        channel data.

    Returns
    -------
    obspy.core.Trace
        trace containing data and metadata.
    """
    stats = obspy.core.Stats(stats)
    stats.channel = channel
    return obspy.core.Trace(data, stats)


def __get_obs_d_from_obs(obs):
    """Get trace containing observatory D component.

    Returns D if found, otherwise computes D from H, E, D0.

    Parameters
    ----------
    obs : obspy.core.Stream
        observatory components (D) or (H, E).

    Returns
    -------
    obspy.core.Trace
        observatory component D.
    """
    try:
        d = obs.select(channel='D')[0]
    except IndexError:
        h = obs.select(channel='H')[0]
        e = obs.select(channel='E')[0]
        d = __get_trace('D', e.stats,
                ChannelConverter.get_obs_d_from_obs(h.data, e.data))
    return d


def __get_obs_e_from_obs(obs):
    """Get trace containing observatory E component.

    Returns E if found, otherwise computes E from H,D.

    Parameters
    ----------
    obs : obspy.core.Stream
        observatory components (E) or (H, D).

    Returns
    -------
    obspy.core.Trace
        observatory component E.
    """
    try:
        e = obs.select(channel='E')[0]
    except IndexError:
        h = obs.select(channel='H')[0]
        d = obs.select(channel='D')[0]
        e = __get_trace('E', d.stats,
                ChannelConverter.get_obs_e_from_obs(h.data, d.data))
    return e
