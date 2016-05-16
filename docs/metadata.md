Trace Metadata
--------------

Metadata is stored in the `Stats` dictionary of each `Trace` object.

- `network`
  Network code.

  Always `NT`

- `station`
  Observatory code.

  Examples:
    `BOU`,
    `BDT`

- `channel`
  Data channel.

  Examples:
    `H`,
    `D`,
    `Z`,
    `F`

- `agency_name`
  Name of agency that operates observatory.

- `station_name`
  Name of observatory.

- `geodetic_latitude`
  Latitude of observatory in decimal degrees [-90, 90].

- `geodetic_longitude`
  Longitude of observatory in decimal degrees [0, 360].

- `elevation`
  Elevation of observatory in meters.

- `sensor_orientation`
  Array of channels recorded by sensor.

- `sensor_sampling_rate`
  How frequently sensor sampled in hertz.

- `data_type`
  Review level of data.

  Examples:
    `definitive`,
    `provisional`,
    `quasi-definitive`,
    `variation`

- `data_interval`
  Time between data samples.
  This is usually set, but more useful properties are `delta` and `sampling_rate`

  Examples:
    `daily`,
    `hourly`,
    `minute`,
    `second`

- `data_interval_type`
  How data interval was produced.

  Examples:
    `average 1 second`,
    `filtered 1-minute (00:15-01:45)`

- `declination_base`
  Observatory declination baseline.

- `is_intermagnet`
  Whether data is available via intermagnet.

- `conditions_of_use`
  Disclaimer for usage.

- `filter_comments`
  Comments about how data was filtered.

- `comments`
  Other comments about this data.
