Readme input output details

## IO Formats ##
There are currently 2 supported file formats for input and output in addition
to Edge server input.

### EDGE ###
--input-edge

### Iaga2002 ###
--input-iaga-file FILENAME
--input-iaga-magweb
--input-iaga-stdin
--input-iaga-url
--output-iaga-file FILENAME
--output-iaga-stdout
--output-iaga-url

### PCDCP ###
--input-pcdcp-file FILENAME
--input-pcdcp-stdin
--input-pcdcp-url
--output-pcdcp-file FILENAME
--output-pcdcp-stdout
--output-pcdcp-url

## IO Methods ##
Several methods exist for retrieving and storing data.

### Edge Server ###
--input-edge HOST PORT

### Single File ###
--input-iaga-file FILENAME
--input-pcdcp-file FILENAME
--output-iaga-file FILENAME
--output-pcdcp-file FILENAME

Specify a single file name for the data to be read from or written to.

### Multiple Files ###
--input-iaga-url
--input-pcdcp-url
--output-iaga-url
--output-pcdcp-url
URLs can be used to fetch or store groups of data using pattern matching. In
order to use a directory of files on a local machine, just specify "file://"
at the beginning of the pattern.

Patterns that will be matched with information from the data:
        - %(i)s       : interval abbreviation (sec, min, hor, etc.)
        - %(interval)s: interval name (second, minute, hour, etc.)
        - %(julian)s  : julian day formatted as JJJ
        - %(obs)s     : lowercase observatory 3-letter code
        - %(OBS)s     : uppercase observatory 3-letter code
        - %(t)s       : type abbreviation (v, d, etc.)
        - %(type)s    : type name (variation, definitive, etc.)
        - %(year)s    : year formatted as YYYY
        - %(ymd)s     : time formatted as YYYYMMDD

Typical IAGA2002 files are stored as `file://./%(obs)s%(ymd)s%(t)%(i)s.%(i)s`
example: bou20130402vmin.min

Typical PCDCP files are stored as `file://./%(OBS)s%(Y)s%(j)s.%(i)s`
example: BOU2013092.min

### Std In and Std Out ###
--input-iaga-stdin
--input-pcdcp-stdin
--output-iaga-stdout
--output-pcdcp-stdout

For standard in, pass the file in with redirection.
