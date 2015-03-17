"""Factory that loads metadata for an observatory"""


# default metadata for the 14 USGS observatories.
DEFAULT_METADATA = {
    'BOU': {
        'station_name': 'Boulder',
        'agency_name': 'United States Geological Survey (USGS)',
        'geodetic_latitude': 40.137,
        'geodetic_longitude': 254.764,
        'elevation': 1682,
        'sensor_orientation': 'HDZF',
        'sensor_sampling_rate': '0.01 second',
        'data_interval_type': 'filtered 1-minute (00:15-01:45)',
        'declination_base': 7406,
        'is_gin': False,
        'is_intermagnet': False,
        'conditions_of_use': 'The Conditions of Use for data provided' +
                ' through INTERMAGNET and acknowledgement templates can be' +
                ' found at www.intermagnet.org',
        'filter_comments': 'Vector 1-minute values are computed from' +
                ' 1-second values using the INTERMAGNET gaussian filter' +
                ' centered on the  minute. Scalar 1-minute values are' +
                ' computed from 1-secondvalues  using the INTERMAGNET' +
                ' gaussian filter centered on the minute. '
    },
    'BRW': {
        'station_name': 'Barrow',
        'agency_name': 'United States Geological Survey (USGS)',
        'geodetic_latitude': 71.322,
        'geodetic_longitude': 203.378,
        'elevation': 12,
        'sensor_orientation': 'HDZF',
        'sensor_sampling_rate': '0.01 second',
        'data_interval_type': 'filtered 1-minute (00:15-01:45)',
        'declination_base': 16000,
        'is_gin': False,
        'is_intermagnet': False,
        'conditions_of_use': 'The Conditions of Use for data provided' +
                ' through INTERMAGNET and acknowledgement templates' +
                ' can be found at www.intermagnet.org',
        'filter_comments': 'Vector 1-minute values are computed from' +
                ' 1-second values using the INTERMAGNET gaussian filter' +
                ' centered on the minute. Scalar 1-minute values are' +
                ' computed from 1-second values using the INTERMAGNET' +
                ' gaussian filter centered on the minute. '
    },
    'BSL': {
        'station_name': 'Stennis Space Center',
        'agency_name': 'United States Geological Survey (USGS)',
        'geodetic_latitude': 30.350,
        'geodetic_longitude': 270.365,
        'elevation': 8,
        'sensor_orientation': 'HDZF',
        'sensor_sampling_rate': '0.01 second',
        'data_interval_type': 'filtered 1-minute (00:15-01:45)',
        'declination_base': 1530,
        'is_gin': False,
        'is_intermagnet': False,
        'conditions_of_use': 'The Conditions of Use for data provided' +
                ' through INTERMAGNET and acknowledgement templates' +
                ' can be found at www.intermagnet.org',
        'filter_comments': 'Vector 1-minute values are computed from' +
                ' 1-second values using the INTERMAGNET gaussian filter' +
                ' centered on the minute. Scalar 1-minute values are' +
                ' computed from 1-second values using the INTERMAGNET' +
                ' gaussian filter centered on the minute. '
    },
    'CMO': {
        'station_name': 'College',
        'agency_name': 'United States Geological Survey (USGS)',
        'geodetic_latitude': 64.874,
        'geodetic_longitude': 212.140,
        'elevation': 197,
        'sensor_orientation': 'HDZF',
        'sensor_sampling_rate': '0.01 second',
        'data_interval_type': 'filtered 1-minute (00:15-01:45)',
        'declination_base': 16876,
        'is_gin': False,
        'is_intermagnet': False,
        'conditions_of_use': 'The Conditions of Use for data provided' +
                ' through INTERMAGNET and acknowledgement templates' +
                ' can be found at www.intermagnet.org',
        'filter_comments': 'Vector 1-minute values are computed from' +
                ' 1-second values using the INTERMAGNET gaussian filter' +
                ' centered on the minute. Scalar 1-minute values are' +
                ' computed from 1-second values using the INTERMAGNET' +
                ' gaussian filter centered on the minute. '
    },
    'DED': {
        'station_name': 'Deadhorse',
        'agency_name': 'United States Geological Survey (USGS)',
        'geodetic_latitude': 70.356,
        'geodetic_longitude': 211.207,
        'elevation': 10,
        'sensor_orientation': 'HDZF',
        'sensor_sampling_rate': '0.01 second',
        'data_interval_type': 'filtered 1-minute (00:15-01:45)',
        'declination_base': 13200,
        'is_gin': False,
        'is_intermagnet': False,
        'conditions_of_use': 'The Conditions of Use for data provided' +
                ' through INTERMAGNET and acknowledgement templates' +
                ' can be found at www.intermagnet.org',
        'filter_comments': 'Vector 1-minute values are computed from' +
                ' 1-second values using the INTERMAGNET gaussian filter' +
                ' centered on the minute. Scalar 1-minute values are' +
                ' computed from 1-second values using the INTERMAGNET' +
                ' gaussian filter centered on the minute. '
    },
    'FRD': {
        'station_name': 'Fredericksburg',
        'agency_name': 'United States Geological Survey (USGS)',
        'geodetic_latitude': 38.205,
        'geodetic_longitude': 282.627,
        'elevation': 69,
        'sensor_orientation': 'HDZF',
        'sensor_sampling_rate': '0.01 second',
        'data_interval_type': 'filtered 1-minute (00:15-01:45)',
        'declination_base': 210942,
        'is_gin': False,
        'is_intermagnet': False,
        'conditions_of_use': 'The Conditions of Use for data provided' +
                ' through INTERMAGNET and acknowledgement templates' +
                ' can be found at www.intermagnet.org',
        'filter_comments': 'Vector 1-minute values are computed from' +
                ' 1-second values using the INTERMAGNET gaussian filter' +
                ' centered on the minute. Scalar 1-minute values are' +
                ' computed from 1-second values using the INTERMAGNET' +
                ' gaussian filter centered on the minute. '
    },
    'FRN': {
        'station_name': 'Fresno',
        'agency_name': 'United States Geological Survey (USGS)',
        'geodetic_latitude': 37.091,
        'geodetic_longitude': 240.282,
        'elevation': 331,
        'sensor_orientation': 'HDZF',
        'data_interval_type': 'filtered 1-minute (00:15-01:45)',
        'declination_base': 9250,
        'is_gin': False,
        'is_intermagnet': False,
        'conditions_of_use': 'The Conditions of Use for data provided' +
                ' through INTERMAGNET and acknowledgement templates' +
                ' can be found at www.intermagnet.org',
        'filter_comments': 'Vector 1-minute values are computed from' +
                ' 1-second values using the INTERMAGNET gaussian filter' +
                ' centered on the minute. Scalar 1-minute values are' +
                ' computed from 1-second values using the INTERMAGNET' +
                ' gaussian filter centered on the minute. '
    },
    'GUA': {
        'station_name': 'Guam',
        'agency_name': 'United States Geological Survey (USGS)',
        'geodetic_latitude': 13.588,
        'geodetic_longitude': 144.867,
        'elevation': 140,
        'sensor_orientation': 'HDZF',
        'sensor_sampling_rate': '0.01 second',
        'data_interval_type': 'filtered 1-minute (00:15-01:45)',
        'declination_base': 1157,
        'is_gin': False,
        'is_intermagnet': False,
        'conditions_of_use': 'The Conditions of Use for data provided' +
                ' through INTERMAGNET and acknowledgement templates' +
                ' can be found at www.intermagnet.org',
        'filter_comments': 'Vector 1-minute values are computed from' +
                ' 1-second values using the INTERMAGNET gaussian filter' +
                ' centered on the minute. Scalar 1-minute values are' +
                ' computed from 1-second values using the INTERMAGNET' +
                ' gaussian filter centered on the minute. '
    },
    'HON': {
        'station_name': 'Honolulu',
        'agency_name': 'United States Geological Survey (USGS)',
        'geodetic_latitude': 21.316,
        'geodetic_longitude': 202.000,
        'elevation': 4,
        'sensor_orientation': 'HDZF',
        'sensor_sampling_rate': '0.01 second',
        'data_interval_type': 'filtered 1-minute (00:15-01:45)',
        'declination_base': 6920,
        'is_gin': False,
        'is_intermagnet': False,
        'conditions_of_use': 'The Conditions of Use for data provided' +
                ' through INTERMAGNET and acknowledgement templates' +
                ' can be found at www.intermagnet.org',
        'filter_comments': 'Vector 1-minute values are computed from' +
                ' 1-second values using the INTERMAGNET gaussian filter' +
                ' centered on the minute. Scalar 1-minute values are' +
                ' computed from 1-second values using the INTERMAGNET' +
                ' gaussian filter centered on the minute. '
    },
    'SHU': {
        'station_name': 'Shumagin',
        'agency_name': 'United States Geological Survey (USGS)',
        'geodetic_latitude': 55.348,
        'geodetic_longitude': 199.538,
        'elevation': 80,
        'sensor_orientation': 'HDZF',
        'sensor_sampling_rate': '0.01 second',
        'data_interval_type': 'filtered 1-minute (00:15-01:45)',
        'declination_base': 13974,
        'is_gin': False,
        'is_intermagnet': False,
        'conditions_of_use': 'The Conditions of Use for data provided' +
                ' through INTERMAGNET and acknowledgement templates' +
                ' can be found at www.intermagnet.org',
        'filter_comments': 'Vector 1-minute values are computed from' +
                ' 1-second values using the INTERMAGNET gaussian filter' +
                ' centered on the minute. Scalar 1-minute values are' +
                ' computed from 1-second values using the INTERMAGNET' +
                ' gaussian filter centered on the minute. '
    },
    'SIT': {
        'station_name': 'Sitka',
        'agency_name': 'United States Geological Survey (USGS)',
        'geodetic_latitude': 57.058,
        'geodetic_longitude': 224.674,
        'elevation': 24,
        'sensor_orientation': 'HDZF',
        'sensor_sampling_rate': '0.01 second',
        'data_interval_type': 'filtered 1-minute (00:15-01:45)',
        'declination_base': 16523,
        'is_gin': False,
        'is_intermagnet': False,
        'conditions_of_use': 'The Conditions of Use for data provided' +
                ' through INTERMAGNET and acknowledgement templates' +
                ' can be found at www.intermagnet.org',
        'filter_comments': 'Vector 1-minute values are computed from' +
                ' 1-second values using the INTERMAGNET gaussian filter' +
                ' centered on the minute. Scalar 1-minute values are' +
                ' computed from 1-second values using the INTERMAGNET' +
                ' gaussian filter centered on the minute. '
    },
    'SJG': {
        'station_name': 'San Juan',
        'agency_name': 'United States Geological Survey (USGS)',
        'geodetic_latitude': 18.113,
        'geodetic_longitude': 293.849,
        'elevation': 424,
        'sensor_orientation': 'HDZF',
        'sensor_sampling_rate': '0.01 second',
        'data_interval_type': 'filtered 1-minute (00:15-01:45)',
        'declination_base': 209800,
        'is_gin': False,
        'is_intermagnet': False,
        'conditions_of_use': 'The Conditions of Use for data provided' +
                ' through INTERMAGNET and acknowledgement templates' +
                ' can be found at www.intermagnet.org',
        'filter_comments': 'Vector 1-minute values are computed from' +
                ' 1-second values using the INTERMAGNET gaussian filter' +
                ' centered on the minute. Scalar 1-minute values are' +
                ' computed from 1-second values using the INTERMAGNET' +
                ' gaussian filter centered on the minute. '
    },
    'TUC': {
        'station_name': 'Tucson',
        'agency_name': 'United States Geological Survey (USGS)',
        'geodetic_latitude': 32.174,
        'geodetic_longitude': 249.267,
        'elevation': 946,
        'sensor_orientation': 'HDZF',
        'sensor_sampling_rate': '0.01 second',
        'data_interval_type': 'filtered 1-minute (00:15-01:45)',
        'declination_base': 7258,
        'is_gin': False,
        'is_intermagnet': False,
        'conditions_of_use': 'The Conditions of Use for data provided' +
                ' through INTERMAGNET and acknowledgement templates' +
                ' can be found at www.intermagnet.org',
        'filter_comments': 'Vector 1-minute values are computed from' +
                ' 1-second values using the INTERMAGNET gaussian filter' +
                ' centered on the minute. Scalar 1-minute values are' +
                ' computed from 1-second values using the INTERMAGNET' +
                ' gaussian filter centered on the minute. '
    }
}

DEFAULT_SENSOR_SAMPLING_RATE = {
        'minute': '0.01 second ',
        'second': '100 Hz'
}

DEFAULT_DATA_INTERVAL_TYPE = {
        'minute': 'filtered 1-minute (00:15-01:45) ',
        'second': 'Average 1-Second'
}


class ObservatoryMetadata(object):
    """Helper class for providing all the metadata needed for a geomag
          timeseries.
    Notes
    -----
    Currently the only method is set_metadata.  Eventually this will probably
    pull from a database, or maybe a config file.
    """

    def __init__(self, metadata=None):
        self.metadata = metadata or DEFAULT_METADATA

    def set_metadata(self, stats, observatory, channel, type, interval):
        """Set timeseries metadata (aka a traces stats)

        Parameters
        ----------
        stats : obspy.core.trace.stats
            the class associated with a given obspy trace, which contains
            it's metadata
        observatory : string
            the observatory code to look up.
        channel : str
            single character channel {H, E, D, Z, F}
        type : {'variation', 'quasi-definitive'}
            data type.
        interval : {'minute', 'second'}
            data interval.

        Returns
        -------
        obspy.core.trace.stats
          the combined stats and the default metadata.
        """
        stats['channel'] = channel
        stats['data_interval'] = interval
        stats['data_type'] = type
        stats['data_interval_type'] = DEFAULT_DATA_INTERVAL_TYPE[interval]
        stats['sensor_sampling_rate'] = DEFAULT_SENSOR_SAMPLING_RATE[interval]
        metadata = self.metadata[observatory]
        for key in metadata:
            if key not in stats:
                stats[key] = metadata[key]
