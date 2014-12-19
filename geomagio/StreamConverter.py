"""Convert streams from one coordinate system to another.

We use three coordinate systems.
Geo: Based on Geographic North.  X, Y, Z, F
     X is north, Y is east, Z is down
Obs: Based on the observatories orientaion. H, E, Z, F, d0
Mag: Based on Magnetic North. H, D, Z, F
"""

import numpy
import obspy.core
import ChannelConverter


def get_geo_from_mag(mag):
    pass


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


def get_mag_from_geo(geo):
    pass


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
    d = __get_obs_d_from_obs(obs)
    z = obs.select(channel='Z')[0]
    f = obs.select(channel='F')[0]
    obs_h = h.data
    obs_d = d.data
    d0 = ChannelConverter.get_radians_from_minutes(
            numpy.float64(d.stats['DECBAS']) / 10)
    (mag_h, mag_d) = ChannelConverter.get_mag_from_obs(obs_h, obs_d, d0)
    return obspy.core.Stream((
            __get_trace('H', h.stats, mag_h),
            __get_trace('D', d.stats, mag_d),
            z, f))


def get_obs_from_geo(geo, include_e=False):
    """Convert a stream to geographic coordinate system.

    Parameters
    ----------
    stream : obspy.core.Stream
        stream containing geographic components X, Y, Z, and F.
    include_e : boolean
        whether to also include the observatory E component.

    Returns
    -------
    obspy.core.Stream
        new stream object containing observatory components H, D, E, Z, and F.
    """
    return get_obs_from_mag(get_mag_from_geo(geo))


def get_obs_from_mag(mag, include_e=False):
    # TODO
    obs = obspy.core.Stream()
    if include_e:
        obs += __get_obs_e_from_obs(obs)
    return obs


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
    except:
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
    except:
        h = obs.select(channel='H')[0]
        d = obs.select(channel='D')[0]
        e = __get_trace('E', d.stats,
                ChannelConverter.get_obs_e_from_obs(h.data, d.data))
    return e
