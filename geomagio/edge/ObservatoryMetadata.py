"""Factory that loads metadata for an observatory"""


# default metadata for the 14 USGS observatories.
DefaultMetadata = {'BOU':
    {'network': 'NT',
    'station': 'BOU',
    'channel': 'H',
    'station_name': 'Boulder',
    'agency_name': 'United States Geological Survey (USGS)',
    'geodetic_latitude': 40.137,
    'geodetic_longitude': 254.764,
    'elevation': 1682,
    'sensor_orientation': 'HDZF',
    'sensor_sampling_rate': '0.01 second',
    'data_type': 'variation',
    'data_interval': 'minute',
    'data_interval_type': 'filtered 1-minute (00:15-01:45)',
    'declination_base': 7406,
    'is_intermagnet': False,
    'condtions_of_use': 'The Conditions of Use for data provided through ' +
        'INTERMAGNET and acknowledgement templates can be found at ' +
        'www.intermagnet.org',
    'filter_comments': 'Vector 1-minute values are computed from 1-second' +
        'values using the INTERMAGNET gaussian filter centered on the ' +
        'minute. Scalar 1-minute values are computed from 1-second values ' +
        'using the INTERMAGNET gaussian filter centered on the minute. ',
    'comments': ' # This data file was constructed by the Golden GIN. Final ' +
        'data will be available on the INTERMAGNET DVD. Go to ' +
        'www.intermagnet.org for details on obtaining this product. '},
'BRW':
    {'network': 'NT',
    'station': 'BRW',
    'channel': 'H',
    'station_name': 'Barrow',
    'agency_name': 'United States Geological Survey (USGS)',
    'geodetic_latitude': 71.322,
    'geodetic_longitude': 203.378,
    'elevation': 12,
    'sensor_orientation': 'HDZF',
    'sensor_sampling_rate': '0.01 second',
    'data_type': 'variation',
    'data_interval': 'minute',
    'data_interval_type': 'filtered 1-minute (00:15-01:45)',
    'declination_base': 16000,
    'is_intermagnet': False,
    'condtions_of_use': 'The Conditions of Use for data provided through ' +
        'INTERMAGNET and acknowledgement templates can be found at ' +
        'www.intermagnet.org',
    'filter_comments': 'Vector 1-minute values are computed from 1-second' +
        'values using the INTERMAGNET gaussian filter centered on the ' +
        'minute. Scalar 1-minute values are computed from 1-second values ' +
        'using the INTERMAGNET gaussian filter centered on the minute. ',
    'comments': ' # This data file was constructed by the Golden GIN. Final ' +
        'data will be available on the INTERMAGNET DVD. Go to ' +
        'www.intermagnet.org for details on obtaining this product. '},
'BSL':
    {'network': 'NT',
    'station': 'BSL',
    'channel': 'H',
    'station_name': 'Stennis Space Center',
    'agency_name': 'United States Geological Survey (USGS)',
    'geodetic_latitude': 30.350,
    'geodetic_longitude': 270.365,
    'elevation': 8,
    'sensor_orientation': 'HDZF',
    'sensor_sampling_rate': '0.01 second',
    'data_type': 'variation',
    'data_interval': 'minute',
    'data_interval_type': 'filtered 1-minute (00:15-01:45)',
    'declination_base': 1530,
    'is_intermagnet': False,
    'condtions_of_use': 'The Conditions of Use for data provided through ' +
        'INTERMAGNET and acknowledgement templates can be found at ' +
        'www.intermagnet.org',
    'filter_comments': 'Vector 1-minute values are computed from 1-second' +
        'values using the INTERMAGNET gaussian filter centered on the ' +
        'minute. Scalar 1-minute values are computed from 1-second values ' +
        'using the INTERMAGNET gaussian filter centered on the minute. ',
    'comments': ' # This data file was constructed by the Golden GIN. Final ' +
        'data will be available on the INTERMAGNET DVD. Go to ' +
        'www.intermagnet.org for details on obtaining this product. '},
'CMO':
    {'network': 'NT',
    'station': 'CMO',
    'channel': 'H',
    'station_name': 'College',
    'agency_name': 'United States Geological Survey (USGS)',
    'geodetic_latitude': 64.874,
    'geodetic_longitude': 212.140,
    'elevation': 197,
    'sensor_orientation': 'HDZF',
    'sensor_sampling_rate': '0.01 second',
    'data_type': 'variation',
    'data_interval': 'minute',
    'data_interval_type': 'filtered 1-minute (00:15-01:45)',
    'declination_base': 16876,
    'is_intermagnet': False,
    'condtions_of_use': 'The Conditions of Use for data provided through ' +
        'INTERMAGNET and acknowledgement templates can be found at ' +
        'www.intermagnet.org',
    'filter_comments': 'Vector 1-minute values are computed from 1-second' +
        'values using the INTERMAGNET gaussian filter centered on the ' +
        'minute. Scalar 1-minute values are computed from 1-second values ' +
        'using the INTERMAGNET gaussian filter centered on the minute. ',
    'comments': ' # This data file was constructed by the Golden GIN. Final ' +
        'data will be available on the INTERMAGNET DVD. Go to ' +
        'www.intermagnet.org for details on obtaining this product. '},
'DED':
    {'network': 'NT',
    'station': 'DED',
    'channel': 'H',
    'station_name': 'Deadhorse',
    'agency_name': 'United States Geological Survey (USGS)',
    'geodetic_latitude': 70.356,
    'geodetic_longitude': 211.207,
    'elevation': 10,
    'sensor_orientation': 'HDZF',
    'sensor_sampling_rate': '0.01 second',
    'data_type': 'variation',
    'data_interval': 'minute',
    'data_interval_type': 'filtered 1-minute (00:15-01:45)',
    'declination_base': 13200,
    'is_intermagnet': False,
    'condtions_of_use': 'The Conditions of Use for data provided through ' +
        'INTERMAGNET and acknowledgement templates can be found at ' +
        'www.intermagnet.org',
    'filter_comments': 'Vector 1-minute values are computed from 1-second' +
        'values using the INTERMAGNET gaussian filter centered on the ' +
        'minute. Scalar 1-minute values are computed from 1-second values ' +
        'using the INTERMAGNET gaussian filter centered on the minute. ',
    'comments': ' # This data file was constructed by the Golden GIN. Final ' +
        'data will be available on the INTERMAGNET DVD. Go to ' +
        'www.intermagnet.org for details on obtaining this product. '},
'FRD':
    {'network': 'NT',
    'station': 'FRD',
    'channel': 'H',
    'station_name': 'Fredericksburg',
    'agency_name': 'United States Geological Survey (USGS)',
    'geodetic_latitude': 38.205,
    'geodetic_longitude': 282.627,
    'elevation': 69,
    'sensor_orientation': 'HDZF',
    'sensor_sampling_rate': '0.01 second',
    'data_type': 'variation',
    'data_interval': 'minute',
    'data_interval_type': 'filtered 1-minute (00:15-01:45)',
    'declination_base': 210942,
    'is_intermagnet': False,
    'condtions_of_use': 'The Conditions of Use for data provided through ' +
        'INTERMAGNET and acknowledgement templates can be found at ' +
        'www.intermagnet.org',
    'filter_comments': 'Vector 1-minute values are computed from 1-second' +
        'values using the INTERMAGNET gaussian filter centered on the ' +
        'minute. Scalar 1-minute values are computed from 1-second values ' +
        'using the INTERMAGNET gaussian filter centered on the minute. ',
    'comments': ' # This data file was constructed by the Golden GIN. Final ' +
        'data will be available on the INTERMAGNET DVD. Go to ' +
        'www.intermagnet.org for details on obtaining this product. '},
'FRN':
    {'network': 'NT',
    'station': 'FRN',
    'channel': 'H',
    'station_name': 'Fresno',
    'agency_name': 'United States Geological Survey (USGS)',
    'geodetic_latitude': 37.091,
    'geodetic_longitude': 240.282,
    'elevation': 331,
    'sensor_orientation': 'HDZF',
    'sensor_sampling_rate': '0.01 second',
    'data_type': 'variation',
    'data_interval': 'minute',
    'data_interval_type': 'filtered 1-minute (00:15-01:45)',
    'declination_base': 9250,
    'is_intermagnet': False,
    'condtions_of_use': 'The Conditions of Use for data provided through ' +
        'INTERMAGNET and acknowledgement templates can be found at ' +
        'www.intermagnet.org',
    'filter_comments': 'Vector 1-minute values are computed from 1-second' +
        'values using the INTERMAGNET gaussian filter centered on the ' +
        'minute. Scalar 1-minute values are computed from 1-second values ' +
        'using the INTERMAGNET gaussian filter centered on the minute. ',
    'comments': ' # This data file was constructed by the Golden GIN. Final ' +
        'data will be available on the INTERMAGNET DVD. Go to ' +
        'www.intermagnet.org for details on obtaining this product. '},
'GUA':
    {'network': 'NT',
    'station': 'GUA',
    'channel': 'H',
    'station_name': 'Guam',
    'agency_name': 'United States Geological Survey (USGS)',
    'geodetic_latitude': 13.588,
    'geodetic_longitude': 144.867,
    'elevation': 140,
    'sensor_orientation': 'HDZF',
    'sensor_sampling_rate': '0.01 second',
    'data_type': 'variation',
    'data_interval': 'minute',
    'data_interval_type': 'filtered 1-minute (00:15-01:45)',
    'declination_base': 1157,
    'is_intermagnet': False,
    'condtions_of_use': 'The Conditions of Use for data provided through ' +
        'INTERMAGNET and acknowledgement templates can be found at ' +
        'www.intermagnet.org',
    'filter_comments': 'Vector 1-minute values are computed from 1-second' +
        'values using the INTERMAGNET gaussian filter centered on the ' +
        'minute. Scalar 1-minute values are computed from 1-second values ' +
        'using the INTERMAGNET gaussian filter centered on the minute. ',
    'comments': ' # This data file was constructed by the Golden GIN. Final ' +
        'data will be available on the INTERMAGNET DVD. Go to ' +
        'www.intermagnet.org for details on obtaining this product. '},
'HON':
    {'network': 'NT',
    'station': 'HON',
    'channel': 'H',
    'station_name': 'Honolulu',
    'agency_name': 'United States Geological Survey (USGS)',
    'geodetic_latitude': 21.316,
    'geodetic_longitude': 202.000,
    'elevation': 4,
    'sensor_orientation': 'HDZF',
    'sensor_sampling_rate': '0.01 second',
    'data_type': 'variation',
    'data_interval': 'minute',
    'data_interval_type': 'filtered 1-minute (00:15-01:45)',
    'declination_base': 6920,
    'is_intermagnet': False,
    'condtions_of_use': 'The Conditions of Use for data provided through ' +
        'INTERMAGNET and acknowledgement templates can be found at ' +
        'www.intermagnet.org',
    'filter_comments': 'Vector 1-minute values are computed from 1-second' +
        'values using the INTERMAGNET gaussian filter centered on the ' +
        'minute. Scalar 1-minute values are computed from 1-second values ' +
        'using the INTERMAGNET gaussian filter centered on the minute. ',
    'comments': ' # This data file was constructed by the Golden GIN. Final ' +
        'data will be available on the INTERMAGNET DVD. Go to ' +
        'www.intermagnet.org for details on obtaining this product. '},
'SHU':
    {'network': 'NT',
    'station': 'SHU',
    'channel': 'H',
    'station_name': 'Shumagin',
    'agency_name': 'United States Geological Survey (USGS)',
    'geodetic_latitude': 55.348,
    'geodetic_longitude': 199.538,
    'elevation': 80,
    'sensor_orientation': 'HDZF',
    'sensor_sampling_rate': '0.01 second',
    'data_type': 'variation',
    'data_interval': 'minute',
    'data_interval_type': 'filtered 1-minute (00:15-01:45)',
    'declination_base': 13974,
    'is_intermagnet': False,
    'condtions_of_use': 'The Conditions of Use for data provided through ' +
        'INTERMAGNET and acknowledgement templates can be found at ' +
        'www.intermagnet.org',
    'filter_comments': 'Vector 1-minute values are computed from 1-second' +
        'values using the INTERMAGNET gaussian filter centered on the ' +
        'minute. Scalar 1-minute values are computed from 1-second values ' +
        'using the INTERMAGNET gaussian filter centered on the minute. ',
    'comments': ' # This data file was constructed by the Golden GIN. Final ' +
        'data will be available on the INTERMAGNET DVD. Go to ' +
        'www.intermagnet.org for details on obtaining this product. '},
'SIT':
    {'network': 'NT',
    'station': 'SIT',
    'channel': 'H',
    'station_name': 'Sitka',
    'agency_name': 'United States Geological Survey (USGS)',
    'geodetic_latitude': 57.058,
    'geodetic_longitude': 224.674,
    'elevation': 24,
    'sensor_orientation': 'HDZF',
    'sensor_sampling_rate': '0.01 second',
    'data_type': 'variation',
    'data_interval': 'minute',
    'data_interval_type': 'filtered 1-minute (00:15-01:45)',
    'declination_base': 16523,
    'is_intermagnet': False,
    'condtions_of_use': 'The Conditions of Use for data provided through ' +
        'INTERMAGNET and acknowledgement templates can be found at ' +
        'www.intermagnet.org',
    'filter_comments': 'Vector 1-minute values are computed from 1-second' +
        'values using the INTERMAGNET gaussian filter centered on the ' +
        'minute. Scalar 1-minute values are computed from 1-second values ' +
        'using the INTERMAGNET gaussian filter centered on the minute. ',
    'comments': ' # This data file was constructed by the Golden GIN. Final ' +
        'data will be available on the INTERMAGNET DVD. Go to ' +
        'www.intermagnet.org for details on obtaining this product. '},
'SJG':
    {'network': 'NT',
    'station': 'SJG',
    'channel': 'H',
    'station_name': 'San Juan',
    'agency_name': 'United States Geological Survey (USGS)',
    'geodetic_latitude': 18.113,
    'geodetic_longitude': 293.849,
    'elevation': 424,
    'sensor_orientation': 'HDZF',
    'sensor_sampling_rate': '0.01 second',
    'data_type': 'variation',
    'data_interval': 'minute',
    'data_interval_type': 'filtered 1-minute (00:15-01:45)',
    'declination_base': 209800,
    'is_intermagnet': False,
    'condtions_of_use': 'The Conditions of Use for data provided through ' +
        'INTERMAGNET and acknowledgement templates can be found at ' +
        'www.intermagnet.org',
    'filter_comments': 'Vector 1-minute values are computed from 1-second' +
        'values using the INTERMAGNET gaussian filter centered on the ' +
        'minute. Scalar 1-minute values are computed from 1-second values ' +
        'using the INTERMAGNET gaussian filter centered on the minute. ',
    'comments': ' # This data file was constructed by the Golden GIN. Final ' +
        'data will be available on the INTERMAGNET DVD. Go to ' +
        'www.intermagnet.org for details on obtaining this product. '},
'TUC':
    {'network': 'NT',
    'station': 'TUC',
    'channel': 'H',
    'station_name': 'Tucson',
    'agency_name': 'United States Geological Survey (USGS)',
    'geodetic_latitude': 32.174,
    'geodetic_longitude': 249.267,
    'elevation': 946,
    'sensor_orientation': 'HDZF',
    'sensor_sampling_rate': '0.01 second',
    'data_type': 'variation',
    'data_interval': 'minute',
    'data_interval_type': 'filtered 1-minute (00:15-01:45)',
    'declination_base': 7258,
    'is_intermagnet': False,
    'condtions_of_use': 'The Conditions of Use for data provided through ' +
        'INTERMAGNET and acknowledgement templates can be found at ' +
        'www.intermagnet.org',
    'filter_comments': 'Vector 1-minute values are computed from 1-second' +
        'values using the INTERMAGNET gaussian filter centered on the ' +
        'minute. Scalar 1-minute values are computed from 1-second values ' +
        'using the INTERMAGNET gaussian filter centered on the minute. ',
    'comments': ' # This data file was constructed by the Golden GIN. Final ' +
        'data will be available on the INTERMAGNET DVD. Go to ' +
        'www.intermagnet.org for details on obtaining this product. '}
}


class ObservatoryMetadata(object):
    """Helper class for providing all the metadata needed for a geomag
          timeseries.
    Notes
    -----
    Currently the only method is set_metadata.  Eventually this will probably
    pull from a database, or maybe a config file.
    """

    def set_metadata(self, stats, observatory, channel, type, interval):
        """Set timeseries metadata (aka a traces stats)

        Parameters
        ----------
        stats : obspy.core.trace.stats
            the class associated with a given obspy trace, which contains
            it's metadata
        observatory : string
            the observatory code to look up.
        type : {'variation', 'quasi-definitive'}
            data type.
        interval : {'minute', 'second'}
            data interval.

        Returns
        -------
        obspy.core.trace.stats
          the combined stats and the default metadata.
        """
        static_stats = DefaultMetadata['BOU']
        for key in static_stats.keys():
            if key not in stats:
                stats[key] = static_stats[key]
        return stats
