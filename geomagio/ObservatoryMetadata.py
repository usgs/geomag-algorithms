"""Factory that loads metadata for an observatory"""


# default metadata for the 14 USGS observatories.
DEFAULT_METADATA = {
    'BDT': {
        'metadata': {
            'station_name': 'Boulder Test',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '40.137',
            'geodetic_longitude': '254.763',
            'elevation': '1682',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 100.0,
            'declination_base': 5527,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45) ',
                'filter_comments': ['Vector 1-minute values are computed' +
                    ' from 1-second values using the INTERMAGNET gaussian' +
                    ' filter centered on the minute. Scalar 1-minute values' +
                    ' are computed from 1-second values using the' +
                    ' INTERMAGNET gaussian filter centered on the minute. ']
            },
            'second': {
                'data_interval_type': 'Average 1-Second'
            }
        }
    },
    'BOU': {
        'metadata': {
            'station_name': 'Boulder',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '40.137',
            'geodetic_longitude': '254.763',
            'elevation': '1682',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 100.0,
            'declination_base': 5527,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45) ',
                'filter_comments': ['Vector 1-minute values are computed' +
                    ' from 1-second values using the INTERMAGNET gaussian' +
                    ' filter centered on the minute. Scalar 1-minute values' +
                    ' are computed from 1-second values using the' +
                    ' INTERMAGNET gaussian filter centered on the minute. ']
            },
            'second': {
                'data_interval_type': 'Average 1-Second'
            }
        }
    },
    'TST': {
        'metadata': {
            'station_name': 'Boulder Test',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '40.137',
            'geodetic_longitude': '254.763',
            'elevation': '1682',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 10000.0,
            'declination_base': 5527,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45) ',
                'filter_comments': ['Vector 1-minute values are computed' +
                    ' from 1-second values using the INTERMAGNET gaussian' +
                    ' filter centered on the minute. Scalar 1-minute values' +
                    ' are computed from 1-second values using the' +
                    ' INTERMAGNET gaussian filter centered on the minute. ']
            },
            'second': {
                'data_interval_type': 'Average 1-Second'
            }
        }
    },
    'BRW': {
        'metadata': {
            'station_name': 'Barrow',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '71.322',
            'geodetic_longitude': '203.378',
            'elevation': '10',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 100.0,
            'declination_base': 10589,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'data_interval_type': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45) ',
                'filter_comments': ['Vector 1-minute values are computed' +
                    ' from 1-second values using the INTERMAGNET gaussian' +
                    ' filter centered on the minute. Scalar 1-minute values' +
                    ' are computed from 1-second values using the' +
                    ' INTERMAGNET gaussian filter centered on the minute. ']
            },
            'second': {
                'data_interval_type': 'Average 1-Second'
            }
        }
    },
    'BRT': {
        'metadata': {
            'station_name': 'Barrow Test',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '71.322',
            'geodetic_longitude': '203.378',
            'elevation': '10',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 10000.0,
            'declination_base': 10589,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'data_interval_type': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45) ',
                'filter_comments': ['Vector 1-minute values are computed' +
                    ' from 1-second values using the INTERMAGNET gaussian' +
                    ' filter centered on the minute. Scalar 1-minute values' +
                    ' are computed from 1-second values using the' +
                    ' INTERMAGNET gaussian filter centered on the minute. ']
            },
            'second': {
                'data_interval_type': 'Average 1-Second'
            }
        }
    },
    'BSL': {
        'metadata': {
            'station_name': 'Stennis Space Center',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '30.350',
            'geodetic_longitude': '270.365',
            'elevation': '8',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 100.0,
            'declination_base': 215772,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45) ',
                'filter_comments': ['Vector 1-minute values are computed' +
                    ' from 1-second values using the INTERMAGNET gaussian' +
                    ' filter centered on the minute. Scalar 1-minute values' +
                    ' are computed from 1-second values using the' +
                    ' INTERMAGNET gaussian filter centered on the minute. ']
            },
            'second': {
                'data_interval_type': 'Average 1-Second'
            }
        }
    },
    'CMO': {
        'metadata': {
            'station_name': 'College',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '64.874',
            'geodetic_longitude': '212.140',
            'elevation': '197',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 100.0,
            'declination_base': 12151,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        }
    },
    'CMT': {
        'metadata': {
            'station_name': 'College',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '64.874',
            'geodetic_longitude': '212.140',
            'elevation': '197',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 10000.0,
            'declination_base': 12151,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        }
    },
    'DED': {
        'metadata': {
            'station_name': 'Deadhorse',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '70.355',
            'geodetic_longitude': '211.207',
            'elevation': '10',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 100.0,
            'declination_base': 10755,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45) ',
                'filter_comments': ['Vector 1-minute values are computed' +
                    ' from 1-second values using the INTERMAGNET gaussian' +
                    ' filter centered on the minute. Scalar 1-minute values' +
                    ' are computed from 1-second values using the' +
                    ' INTERMAGNET gaussian filter centered on the minute. ']
            },
            'second': {
                'data_interval_type': 'Average 1-Second'
            }
        }
    },
    'DHT': {
        'metadata': {
            'station_name': 'Deadhorse Test',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '70.355',
            'geodetic_longitude': '211.207',
            'elevation': '10',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 10000.0,
            'declination_base': 10755,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45) ',
                'filter_comments': ['Vector 1-minute values are computed' +
                    ' from 1-second values using the INTERMAGNET gaussian' +
                    ' filter centered on the minute. Scalar 1-minute values' +
                    ' are computed from 1-second values using the' +
                    ' INTERMAGNET gaussian filter centered on the minute. ']
            },
            'second': {
                'data_interval_type': 'Average 1-Second'
            }
        }
    },
    'FRD': {
        'metadata': {
            'station_name': 'Fredericksburg',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '38.205',
            'geodetic_longitude': '282.627',
            'elevation': '69',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 100.0,
            'declination_base': 209690,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45) ',
                'filter_comments': ['Vector 1-minute values are computed' +
                    ' from 1-second values using the INTERMAGNET gaussian' +
                    ' filter centered on the minute. Scalar 1-minute values' +
                    ' are computed from 1-second values using the' +
                    ' INTERMAGNET gaussian filter centered on the minute. ']
            },
            'second': {
                'data_interval_type': 'Average 1-Second'
            }
        }
    },
    'FDT': {
        'metadata': {
            'station_name': 'Fredericksburg Test',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '38.205',
            'geodetic_longitude': '282.627',
            'elevation': '69',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 100.0,
            'declination_base': 209690,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45) ',
                'filter_comments': ['Vector 1-minute values are computed' +
                    ' from 1-second values using the INTERMAGNET gaussian' +
                    ' filter centered on the minute. Scalar 1-minute values' +
                    ' are computed from 1-second values using the' +
                    ' INTERMAGNET gaussian filter centered on the minute. ']
            },
            'second': {
                'data_interval_type': 'Average 1-Second'
            }
        }
    },
    'FRN': {
        'metadata': {
            'station_name': 'Fresno',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '37.091',
            'geodetic_longitude': '240.282',
            'elevation': '331',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 100.0,
            'declination_base': 8097,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45) ',
                'filter_comments': ['Vector 1-minute values are computed' +
                    ' from 1-second values using the INTERMAGNET gaussian' +
                    ' filter centered on the minute. Scalar 1-minute values' +
                    ' are computed from 1-second values using the' +
                    ' INTERMAGNET gaussian filter centered on the minute. ']
            },
            'second': {
                'data_interval_type': 'Average 1-Second'
            }
        }
    },
    'GUA': {
        'metadata': {
            'station_name': 'Guam',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '13.588',
            'geodetic_longitude': '144.867',
            'elevation': '140',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 100.0,
            'declination_base': 764,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45) ',
                'filter_comments': ['Vector 1-minute values are computed' +
                    ' from 1-second values using the INTERMAGNET gaussian' +
                    ' filter centered on the minute. Scalar 1-minute values' +
                    ' are computed from 1-second values using the' +
                    ' INTERMAGNET gaussian filter centered on the minute. ']
            },
            'second': {
                'data_interval_type': 'Average 1-Second'
            }
        }
    },
    'HON': {
        'metadata': {
            'station_name': 'Honolulu',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '21.316',
            'geodetic_longitude': '202.000',
            'elevation': '4',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 100.0,
            'declination_base': 5982,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45) ',
                'filter_comments': ['Vector 1-minute values are computed' +
                    ' from 1-second values using the INTERMAGNET gaussian' +
                    ' filter centered on the minute. Scalar 1-minute values' +
                    ' are computed from 1-second values using the' +
                    ' INTERMAGNET gaussian filter centered on the minute. ']
            },
            'second': {
                'data_interval_type': 'Average 1-Second'
            }
        }
    },
    'KAK': {
        'metadata': {
            'station_name': 'Kakioka',
            'agency_name': 'Japan Meteorological Agency',
            'geodetic_latitude': '36.232',
            'geodetic_longitude': '140.186',
            'elevation': '36',
            'sensor_orientation': 'HDZF',
            'reported': 'HDZF',
            'sensor_sampling_rate': 0.01,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45)'
            },
            'second': {
                'data_interval_type': ''
            }
        }
    },
    'NEW': {
        'metadata': {
            'station_name': 'Newport',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '48.265',
            'geodetic_longitude': '242.878',
            'elevation': '770',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 100.0,
            'declination_base': 9547,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45) ',
                'filter_comments': ['Vector 1-minute values are computed' +
                    ' from 1-second values using the INTERMAGNET gaussian' +
                    ' filter centered on the minute. Scalar 1-minute values' +
                    ' are computed from 1-second values using the' +
                    ' INTERMAGNET gaussian filter centered on the minute. ']
            },
            'second': {
                'data_interval_type': 'Average 1-Second'
            }
        }
    },
    'SHU': {
        'metadata': {
            'station_name': 'Shumagin',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '55.348',
            'geodetic_longitude': '199.538',
            'elevation': '80',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 100.0,
            'declination_base': 7386,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45) ',
                'filter_comments': ['Vector 1-minute values are computed' +
                    ' from 1-second values using the INTERMAGNET gaussian' +
                    ' filter centered on the minute. Scalar 1-minute values' +
                    ' are computed from 1-second values using the' +
                    ' INTERMAGNET gaussian filter centered on the minute. ']
            },
            'second': {
                'data_interval_type': 'Average 1-Second'
            }
        }
    },
    'SIT': {
        'metadata': {
            'station_name': 'Sitka',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '57.058',
            'geodetic_longitude': '224.675',
            'elevation': '24',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 100.0,
            'declination_base': 12349,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45) ',
                'filter_comments': ['Vector 1-minute values are computed' +
                    ' from 1-second values using the INTERMAGNET gaussian' +
                    ' filter centered on the minute. Scalar 1-minute values' +
                    ' are computed from 1-second values using the' +
                    ' INTERMAGNET gaussian filter centered on the minute. ']
            },
            'second': {
                'data_interval_type': 'Average 1-Second'
            }
        }
    },
    'SJG': {
        'metadata': {
            'station_name': 'San Juan',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '18.113',
            'geodetic_longitude': '293.849',
            'elevation': '424',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 100.0,
            'declination_base': 208439,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45) ',
                'filter_comments': ['Vector 1-minute values are computed' +
                    ' from 1-second values using the INTERMAGNET gaussian' +
                    ' filter centered on the minute. Scalar 1-minute values' +
                    ' are computed from 1-second values using the' +
                    ' INTERMAGNET gaussian filter centered on the minute. ']
            },
            'second': {
                'data_interval_type': 'Average 1-Second'
            }
        }
    },
    'TUC': {
        'metadata': {
            'station_name': 'Tucson',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '32.174',
            'geodetic_longitude': '249.267',
            'elevation': '946',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 100.0,
            'declination_base': 5863,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45) ',
                'filter_comments': ['Vector 1-minute values are computed' +
                    ' from 1-second values using the INTERMAGNET gaussian' +
                    ' filter centered on the minute. Scalar 1-minute values' +
                    ' are computed from 1-second values using the' +
                    ' INTERMAGNET gaussian filter centered on the minute. ']
            },
            'second': {
                'data_interval_type': 'Average 1-Second'
            }
        }
    },
    'USGS': {
        'metadata': {
            'station_name': 'USGS',
            'agency_name': 'United States Geological Survey (USGS)',
            'geodetic_latitude': '40.137',
            'geodetic_longitude': '254.764',
            'elevation': '1682',
            'sensor_orientation': 'HDZF',
            'sensor_sampling_rate': 100.0,
            'declination_base': 0,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': '1-minute calculated',
                'filter_comments': []
            },
            'hourly': {
                'data_interval_type': '1-hour calculated'
            }
        }
    },
    'BLC': {
        'metadata': {
            'station_name': 'Baker Lake',
            'agency_name': 'Geological Survey of Canada (GSC)',
            'geodetic_latitude': '64.300',
            'geodetic_longitude': '264.000',
            'elevation': '0',
            'sensor_orientation': 'XYZF',
            'reported': 'XYZF',
            'sensor_sampling_rate': 100.0,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45)'
            },
            'second': {
                'data_interval_type': ''
            }
        }
    },
    'BRD': {
        'metadata': {
            'station_name': 'Brandon',
            'agency_name': 'Geological Survey of Canada (GSC)',
            'geodetic_latitude': '49.600',
            'geodetic_longitude': '262.900',
            'elevation': '0',
            'sensor_orientation': 'XYZF',
            'reported': 'XYZF',
            'sensor_sampling_rate': 100.0,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45)'
            },
            'second': {
                'data_interval_type': ''
            }
        }
    },
    'CBB': {
        'metadata': {
            'station_name': 'Cambridge Bay',
            'agency_name': 'Geological Survey of Canada (GSC)',
            'geodetic_latitude': '69.200',
            'geodetic_longitude': '255.000',
            'elevation': '0',
            'sensor_orientation': 'XYZF',
            'reported': 'XYZF',
            'sensor_sampling_rate': 100.0,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45)'
            },
            'second': {
                'data_interval_type': ''
            }
        }
    },
    'EUA': {
        'metadata': {
            'station_name': 'Eureka',
            'agency_name': 'Geological Survey of Canada (GSC)',
            'geodetic_latitude': '55.300',
            'geodetic_longitude': '282.300',
            'elevation': '0',
            'sensor_orientation': 'XYZF',
            'reported': 'XYZF',
            'sensor_sampling_rate': 100.0,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45)'
            },
            'second': {
                'data_interval_type': ''
            }
        }
    },
    'FCC': {
        'metadata': {
            'station_name': 'Fort Churchill',
            'agency_name': 'Geological Survey of Canada (GSC)',
            'geodetic_latitude': '58.800',
            'geodetic_longitude': '265.900',
            'elevation': '0',
            'sensor_orientation': 'XYZF',
            'reported': 'XYZF',
            'sensor_sampling_rate': 100.0,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45)'
            },
            'second': {
                'data_interval_type': ''
            }
        }
    },
    'HAD': {
        'metadata': {
            'station_name': 'Hartland',
            'agency_name': 'British Geological Survey (BGS)',
            'geodetic_latitude': '51.000',
            'geodetic_longitude': '355.500',
            'elevation': '0',
            'sensor_orientation': 'HDZF',
            'reported': 'HDZF',
            'sensor_sampling_rate': 100.0,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45)'
            },
            'second': {
                'data_interval_type': ''
            }
        }
    },
    'HER': {
        'metadata': {
            'station_name': 'Hermanus',
            'agency_name': 'National Research Foundation',
            'geodetic_latitude': '-34.400',
            'geodetic_longitude': '19.200',
            'elevation': '0',
            'sensor_orientation': 'HDZF',
            'reported': 'HDZF',
            'sensor_sampling_rate': 100.0,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45)'
            },
            'second': {
                'data_interval_type': ''
            }
        }
    },
    'IQA': {
        'metadata': {
            'station_name': 'Iqaluit',
            'agency_name': 'Geological Survey of Canada (GSC)',
            'geodetic_latitude': '63.800',
            'geodetic_longitude': '291.500',
            'elevation': '0',
            'sensor_orientation': 'XYZF',
            'reported': 'XYZF',
            'sensor_sampling_rate': 100.0,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45)'
            },
            'second': {
                'data_interval_type': ''
            }
        }
    },
    'MEA': {
        'metadata': {
            'station_name': 'Meanook',
            'agency_name': 'Geological Survey of Canada (GSC)',
            'geodetic_latitude': '54.600',
            'geodetic_longitude': '246.700',
            'elevation': '0',
            'sensor_orientation': 'XYZF',
            'reported': 'XYZF',
            'sensor_sampling_rate': 100.0,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45)'
            },
            'second': {
                'data_interval_type': ''
            }
        }
    },
    'OTT': {
        'metadata': {
            'station_name': 'Ottowa',
            'agency_name': 'Geological Survey of Canada (GSC)',
            'geodetic_latitude': '45.400',
            'geodetic_longitude': '284.500',
            'elevation': '0',
            'sensor_orientation': 'XYZF',
            'reported': 'XYZF',
            'sensor_sampling_rate': 100.0,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45)'
            },
            'second': {
                'data_interval_type': ''
            }
        }
    },
    'RES': {
        'metadata': {
            'station_name': 'Resolute Bay',
            'agency_name': 'Geological Survey of Canada (GSC)',
            'geodetic_latitude': '74.700',
            'geodetic_longitude': '265.100',
            'elevation': '0',
            'sensor_orientation': 'XYZF',
            'reported': 'XYZF',
            'sensor_sampling_rate': 100.0,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45)'
            },
            'second': {
                'data_interval_type': ''
            }
        }
    },
    'SNK': {
        'metadata': {
            'station_name': 'Sanikiluaq',
            'agency_name': 'Geological Survey of Canada (GSC)',
            'geodetic_latitude': '62.400',
            'geodetic_longitude': '245.500',
            'elevation': '0',
            'sensor_orientation': 'XYZF',
            'reported': 'XYZF',
            'sensor_sampling_rate': 100.0,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45)'
            },
            'second': {
                'data_interval_type': ''
            }
        }
    },
    'STJ': {
        'metadata': {
            'station_name': 'St Johns',
            'agency_name': 'Geological Survey of Canada (GSC)',
            'geodetic_latitude': '47.600',
            'geodetic_longitude': '307.300',
            'elevation': '0',
            'sensor_orientation': 'XYZF',
            'reported': 'XYZF',
            'sensor_sampling_rate': 100.0,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45)'
            },
            'second': {
                'data_interval_type': ''
            }
        }
    },
    'VIC': {
        'metadata': {
            'station_name': 'Victoria',
            'agency_name': 'Geological Survey of Canada (GSC)',
            'geodetic_latitude': '48.600',
            'geodetic_longitude': '236.600',
            'elevation': '0',
            'sensor_orientation': 'XYZF',
            'reported': 'XYZF',
            'sensor_sampling_rate': 100.0,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45)'
            },
            'second': {
                'data_interval_type': ''
            }
        }
    },
    'YKC': {
        'metadata': {
            'station_name': 'Yellowknife',
            'agency_name': 'Geological Survey of Canada (GSC)',
            'geodetic_latitude': '62.400',
            'geodetic_longitude': '245.500',
            'elevation': '0',
            'sensor_orientation': 'XYZF',
            'reported': 'XYZF',
            'sensor_sampling_rate': 100.0,
            'is_gin': False,
            'is_intermagnet': False,
            'conditions_of_use': 'The Conditions of Use for data provided' +
                    ' through INTERMAGNET and acknowledgement templates' +
                    ' can be found at www.intermagnet.org'
        },
        'interval_specific': {
            'minute': {
                'data_interval_type': 'filtered 1-minute (00:15-01:45)'
            },
            'second': {
                'data_interval_type': ''
            }
        }
    }
}


DEFAULT_INTERVAL_SPECIFIC = {
        'minute': {'data_interval_type': 'filtered 1-minute (00:15-01:45) '},
        'second': {'data_interval_type': 'Average 1-Second'}
}


class ObservatoryMetadata(object):
    """Helper class for providing all the metadata needed for a geomag
          timeseries.
    Notes
    -----
    Currently the only method is set_metadata.  Eventually this will probably
    pull from a database, or maybe a config file.
    """

    def __init__(self, metadata=None, interval_specific=None):
        self.metadata = metadata or DEFAULT_METADATA
        self.interval_specific = interval_specific or \
                DEFAULT_INTERVAL_SPECIFIC

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
        if observatory not in self.metadata:
            return
        # copy in standard metadata
        metadata = self.metadata[observatory]['metadata']
        for key in metadata:
            stats[key] = metadata[key]
        # copy in interval specific metadata
        interval_specific = self.interval_specific
        if 'interval_specific' in self.metadata[observatory]:
            interval_specific = \
                self.metadata[observatory]['interval_specific']
        # stats['data_interval_type'] = data_interval_type[interval]
        if interval in interval_specific:
            for key in interval_specific[interval]:
                stats[key] = interval_specific[interval][key]
