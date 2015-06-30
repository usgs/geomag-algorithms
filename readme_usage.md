Readme usage details

## Usage ##

Running `geomag.py -h` or `geomag.py --help` will show an extensive list of
input parameters.

Some of the key parameters that should be specified are listed here along with
examples.

`--starttime STARTTIME`
`--endtime ENDTIME`
Start and End times accept several time formats including ISO
(`YYYY-MM-DDTHH:MM:SSZ`)
To retrieve data for all of the month of January 2015
`--starttime 2015-01-01T00:00:00Z --endtime 2015-01-31T23:59:59Z`

To retrieve all _raw_ (variation) _H_, _E_, _Z_ and _F_ _minute_ data from
_Boulder Observatory_ for the entire day of _July 1st 2014_ from an _iaga2002_
formatted file and output it to a _PCDCP_ formatted file:
```
geomag.py --type variation --inchannels H E Z F --interval minute --observatory BOU
--starttime 2014-07-01T00:00:00Z --endtime 2014-07-01T23:59:00Z
--input-iaga-file BOU20140701vmin.min --output-pcdcp-file BOU2014182.min
```
