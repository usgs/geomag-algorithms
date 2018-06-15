"""SNCL utilities.

Station
Network
Channel
Location
"""

CHANNEL_FROM_COMPONENT = {
    # e-field
    'E-E':  'QX',
    'E-N':  'QY',
    'E-U':  'QU',
    'E-V':  'QV',
    # derived indicies
    'AE':   'XA',
    'DST3': 'X3',
    'DST':  'X4',
    'K':    'XK'
}
COMPONENT_FROM_CHANNEL = dict((v,k) for (k,v) in CHANNEL_FROM_COMPONENT.iteritems())


class SNCLException(Exception):
    pass


def get_scnl(observatory,
        component=None,
        channel=None,
        data_type='variation',
        location=None,
        interval='second',
        network='NT'):
    # use explicit channel/location if specified
    channel = channel or __get_channel(component, interval)
    location = location or __get_location(component, data_type)
    return {
        'station': observatory,
        'network': network,
        'channel': channel,
        'location': location,
    }

def parse_sncl(sncl):
    network = sncl['network']
    station = sncl['station']
    channel = sncl['channel']
    location = sncl['location']
    return {
        'observatory': station,
        'network': network,
        'component': __parse_component(channel, location),
        'data_type': __parse_data_type(location),
        'interval': __parse_interval(channel),
    }


def __get_channel(component, interval):
    channel_start = __get_channel_start(interval)
    # check for direct component mappings
    if component in CHANNEL_FROM_COMPONENT:
        channel_end = CHANNEL_FROM_COMPONENT[component]
    else:
        channel_end = __get_channel_end(component)
    return channel_start + channel_end

def __get_channel_start(interval):
    if interval == '10hertz' or interval == 0.1:
        return 'B'
    if interval == 'second' or interval == 1:
        return 'L'
    if interval == 'minute' or interval == 60:
        return 'U'
    if interval == 'hour' or interval == 3600:
        return 'R'
    if interval == 'day' or interval == 86400:
        return 'P'
    raise SNCLException('Unexpected interval {}'.format(interval))

def __get_channel_end(component):
    # default to engineering units
    channel_middle = 'F'
    # check for suffix that may override
    component_parts = component.split('-')
    channel_end = component_parts[0]
    if len(component_parts) > 1:
        component_suffix = component_parts[1]
        if component_suffix == '-Bin':
            channel_middle = 'Y'
        elif component_suffix == '-Temp':
            channel_middle = 'K'
        elif component_suffix == '-Volt':
            channel_middle = 'E'
        else:
            raise SNCLException('Unexpected component {}'.format(component))
    return channel_middle + channel_end


def __get_location(component, data_type):
    location_start = __get_location_start(data_type)
    location_end = __get_location_end(component)
    return location_start + location_end

def __get_location_start(data_type):
    if data_type == 'variation':
        return 'R'
    elif data_type == 'adjusted':
        return 'A'
    elif data_type == 'quasi-definitive':
        return 'Q'
    elif data_type == 'definitive':
        return 'D'
    raise SNCLException('Unexpected data type {}'.format(data_type))

def __get_location_end(component):
    if component.endswith('-Sat'):
        return '1'
    if component.endswith('-Dist'):
        return 'D'
    if component.endswith('-SQ'):
        return 'Q'
    if component.endswith('-SV'):
        return 'V'
    return '0'


def __parse_component(channel, location):
    channel_end = channel[1:]
    if channel_end in COMPONENT_FROM_CHANNEL:
        return COMPONENT_FROM_CHANNEL[channel_end]
    channel_middle = channel[1]
    component = channel[2]
    component_end = ''
    if channel_middle == 'E':
        component_end = '-Volt'
    elif channel_middle == 'K':
        component_end = '-Temp'
    elif channel_middle == 'Y':
        component_end = '-Bin'
    elif channel_middle == 'F':
        component_end = __parse_component_end(location)
    else:
        raise SNCLException('Unexpected channel middle {}'.format(channel))
    return component + component_end

def __parse_component_end(location):
    location_end = location[1]
    if location_end == '0':
        return ''
    if location_end == '1':
        return '-Sat'
    if location_end == 'D':
        return '-Dist'
    if location_end == 'Q':
        return '-SQ'
    if location_end == 'V':
        return '-SV'
    raise SNCLException('Unexpected location end {}'.format(location_end))

def __parse_data_type(location):
    location_start = location[0]
    if location_start == 'R':
        return 'variation'
    if location_start == 'A':
        return 'adjusted'
    if location_start == 'Q':
        return 'quasi-definitive'
    if location_start == 'D':
        return 'definitive'
    raise SNCLException('Unexpected location start {}'.format(location_start))

def __parse_interval(channel):
    channel_start = channel[0]
    if channel_start == 'B':
        return 0.1
    if channel_start == 'L':
        return 1
    if channel_start == 'U':
        return 60
    if channel_start == 'R':
        return 3600
    if channel_start == 'P':
        return 86400
    raise SNCLException('Unexpected channel {}'.format(channel))
