Readme input output details

## IO Formats ##
There are currently 2 supported file formats for input and output in addition
to Edge server input.

#### EDGE ####

`--input-edge HOST PORT`
Specify an IP address or host name where your Edge lives along with a port.

#### Iaga2002 ####

`--input-iaga-file FILENAME`
Specify the name of the file to read from.

`--input-iaga-magweb`
Data will be pulled from geomag.usgs.gov/data/magnetometer if it exists.

`--input-iaga-stdin`
Use redirection on the command line to send your data in.

`--input-iaga-url`
Use a file pattern to read from multiple IAGA2002 files.

`--output-iaga-file FILENAME`
Specify the name of the file to write to.

`--output-iaga-stdout`
Output will be send directly to the command line.

`--output-iaga-url`
Use a file pattern to write to multiple IAGA2002 files.

#### IMFV283 ####

`--input-imfv283-file FILENAME`
Specify the name of the file to read from.

`--input-imfv283-stdin`
Use redirection on the command line to send your data in.

`--input-imfv283-url`
Use a file pattern to read IMFV283 file.

#### PCDCP ####

`--input-pcdcp-file FILENAME`
Specify the name of the file to read from.

`--input-pcdcp-stdin`
Use redirection on the command line to send your data in.

`--input-pcdcp-url`
Use a file pattern to read from multiple PCDCP files.

`--output-pcdcp-file FILENAME`
Specify the name of the file to write to.

`--output-pcdcp-stdout`
Output will be send directly to the command line.

`--output-pcdcp-url`
Use a file pattern to write to multiple PCDCP files.


## IO Methods ##
Several methods exist for retrieving and storing data.

#### Edge Server ####

`--input-edge HOST PORT`
Specify an IP address or host name where your Edge lives along with a port.

#### Single File ####

`--input-iaga-file FILENAME`
`--input-pcdcp-file FILENAME`
`--output-iaga-file FILENAME`
`--output-pcdcp-file FILENAME`
Specify a single file name for the data to be read from or written to.

#### Multiple Files ####

`--input-iaga-url`
`--input-pcdcp-url`
`--output-iaga-url`
`--output-pcdcp-url`
URLs can be used to fetch or store groups of data using pattern matching. In
order to use a directory of files on a local machine, just specify "file://"
at the beginning of the pattern.

Patterns that will be matched with information from the data:

  - __%(i)s__       : interval abbreviation (sec, min, hor, etc.)
  - __%(interval)s__: interval name (second, minute, hour, etc.)
  - __%(julian)s__  : julian day formatted as JJJ
  - __%(obs)s__     : lowercase observatory 3-letter code
  - __%(OBS)s__     : uppercase observatory 3-letter code
  - __%(t)s__       : type abbreviation (v, q, d, etc.)
  - __%(type)s__    : type name (variation, quasi-definitive, definitive, etc.)
  - __%(year)s__    : year formatted as YYYY
  - __%(ymd)s__     : time formatted as YYYYMMDD

Typical IAGA2002 files are stored as `file://./%(obs)s%(ymd)s%(t)%(i)s.%(i)s`

Example: bou20130402vmin.min

Typical PCDCP files are stored as `file://./%(OBS)s%(Y)s%(j)s.%(i)s`

Example: BOU2013092.min

#### Std In and Std Out ####

`--input-iaga-stdin`
`--input-pcdcp-stdin`
`--output-iaga-stdout`
`--output-pcdcp-stdout`

For standard in, pass the data in with redirection.
