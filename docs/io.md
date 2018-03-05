IO Formats
==========


## Input

### Input Format

`--input {edge, goes, iaga2002, imfv283, pcdcp}`
Specify input format.

`edge`
  EDGE/Earthworm server.

`iaga2002`
  IAGA2002 format.

`imfv283`
  IMFV283 binary format.

`pcdcp`
  PCDCP format.


### Input Source
For input format `edge`

`--input-host HOST`
  (Default `cwbpub.cr.usgs.gov`)

`--input-port PORT`
  (Default `2060`)

For input formats `iaga2002`, `imfv283`, `pcdcp`

`--input-file FILE`
  Read from a specific file.

`--input-stdin`
  Read from standard input

`--input-url URLTEMPLATE`
  Read one or more files using a pattern.

`--input-url-interval URLINTERVAL`
  (Default `86400` seconds)

Interval specifies the amount of data in each url and defaults to 1 day.



## Output

### Output Format

`--output {binlog, edge, iaga2002, imfjson, pcdcp, plot, temperature, vbf}`

Specify output format.

`binlog`
  BINLOG format.

`edge`
  EDGE server.

`iaga2002`
  IAGA2002 format.

`imfjson`
  IMFJSON format.

`pcdcp`
  PCDCP format.

`plot`
  Interactive matplotlib plot.

`temperature`
  Temperature file format.

`vbf`
  Volt/Bin format.


### Output Target
For output format `edge`

`--output-edge-read-port PORT`
  (Default `2060`)
  Port used when checking for output gaps to fill.

`--output-edge-forceout`
  Force miniseed blocks to be written instead of waiting for more data.

`--output-edge-tag TAG`
  (Default `GEOMAG`)
  Unique identifier used for data being loaded.

`--output-host HOST`
  (Default `cwbpub.cr.usgs.gov`)

`--output-port PORT`
  (Default `2060`)

For output formats `binlog`, `iaga2002`, `pcdcp`, `temperature`, `vbf`

`--output-file FILE`
  Write to a specific file.

`--output-stdout`
  Write to standard output

`--output-url URLTEMPLATE`
  Write one or more files using a pattern.

  Only "file://" urls are currently supported for output.

`--output-url-interval URLINTERVAL`
  (Default `86400` seconds)


## URL Templates

URLs can be used to fetch or store groups of data using pattern matching. In
order to use a directory of files on a local machine, just specify "file://"
at the beginning of the pattern.

NOTE: Any protocols supported by the systems `libcurl` are also supported
by this application.  Certain protocols like 'sftp' require you to manually
connect and accept the remove servers key fingerprint before they will work
in a url template.

`--input-url URLTEMPLATE`

`--output-url URLTEMPLATE`

Patterns that will be matched with information from the data:

| Key           | Purpose                                                  |
| ------------- | -------------------------------------------------------- |
| __date__      | datetime object, for custom strftime format patterns     |
| __i__         | interval abbreviation (sec, min, hor, etc.)              |
| __interval__  | interval name (second, minute, hour, etc.)               |
| __minute__    | minute of day                                            |
| __month__     | lower case abbreviated month name                        |
| __MONTH__     | upper case abbreviated month name                        |
| __obs__       | lowercase observatory 3-letter code                      |
| __OBS__       | uppercase observatory 3-letter code                      |
| __t__         | type abbreviation (v, q, d, etc.)                        |
| __type__      | type name (variation, quasi-definitive, definitive, etc.)|
| _julian_      | deprecated. julian day formatted as JJJ                  |
| _year_        | deprecated. year formatted as YYYY                       |
| _ymd_         | deprecated. time formatted as YYYYMMDD                   |


These patterns can be used with python string formatting (_recommended_),
or older string interpolation (for backward compatibility).

See http://strftime.org/ for a list of available date format options.

### IAGA2002 example
- `file://./{obs}{date:%Y%m%d}{t}{i}.{i}` (string formatting, _recommended_)
- `file://./%(obs)s%(ymd)s%(t)%(i)s.%(i)s` (string interpolation)

For date=2013-04-02, type=variation, interval=minute, the resulting url is

`file://./bou20130402vmin.min`


### PCDCP example:
- `file://./{OBS}/{date:%Y%j}.{i}` (string formatting, _recommended_)
- `file://./%(OBS)s/%(Y)s%(j)s.%(i)s` (string interpolation)

For date=2013-04-02, type=variation, interval=minute, the resulting url is

`file://./BOU2013092.min`


## URL Interval

`--input-url-interval INTERVAL`

`--output-url-interval INTERVAL`


The default URL Interval is `86400` seconds, which results in a separate url
for each day.  The url template is called once for each interval
(intervals start at unix epoch 1970-01-01T00:00:00Z).

Examples
  `600` - 10 minutes per url
- `3600` - one hour per url
- `604800` - 7 days per url

When customizing the interval, be sure the URL Template is unique for each
interval otherwise urls may overlap and lead to undesirable results.
