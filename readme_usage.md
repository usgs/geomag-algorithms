Readme usage details

## Usage ##

You can install the project if you haven't already with

      pip install git+https://github.com/usgs/geomag-algorithms.git

Running `geomag.py -h` or `geomag.py --help` will show an extensive list of
input parameters.

Some of the key parameters that should be specified are listed here along with
examples. They include

 - __start time__           - YYYY-MM-DDTHH:MM:SSZ
 - __end time__             - YYYY-MM-DDTHH:MM:SSZ
 - __observatory code__     - 3-letter observatory code
 - __data input source__    - {--input-edge, --input-iaga-file, ...}
 - __data output source__   - {--output-pcdcp-url, --output-iaga-file, ...}
 - __input data channels__  - {[CHANNEL [CHANNEL ...]]}
 - __output data channels__ - {[CHANNEL [CHANNEL ...]]}
 - __data type__            - {variation, quasi-definitive, definitive}
 - __interval__             - {minute, second, hour, day}

### Examples ###

To retrieve all _raw_ (variation) _H_, _E_, _Z_ and _F_ _minute_ data from
_Boulder Observatory_ for the entire day of _July 1st 2014_ from an _iaga2002_
formatted file and output _H_, _E_, _Z_ and _F_ data to a _PCDCP_ formatted
file:

      geomag.py --type variation --inchannels H E Z F --interval minute \
      --observatory BOU \
      --starttime 2014-07-01T00:00:00Z \
      --endtime 2014-07-01T23:59:00Z \
      --input-iaga-file BOU20140701vmin.min \
      --outchannels H E Z F \
      --output-pcdcp-file BOU2014182.min

To retrieve all _raw_ (variation) _H_, _E_, _Z_ and _F_ _minute_ data from
_Tucson Observatory_ for the entire month of _March 2013_ from _pcdcp_
formatted files in a "data-pcdcp" directory and output _H_, _E_, _Z_ and _F_
data to a group of _iaga2002_ formatted files in a "data-iaga" directory:

      geomag.py --type variation --inchannels H E Z F --interval minute \
      --observatory TUC \
      --starttime 2013-03-01T00:00:00Z \
      --endtime 2013-03-31T23:59:00Z \
      --input-pcdcp-url file://data-pcdcp/./%(OBS)s%(year)s%(julian)s.%(i)s \
      --output-iaga-url file://data-iaga/./$(obs)s%(Y)s%(j)s.%(i)s \
      --outchannels H E Z F


---
### Algorithms ###

There are flags to specify certain algorithms should be run against the data.

#### XYZ ####

`--xyz {geo, mag, obs, obsd} {geo, mag, obs, obsd}`

#### [XYZ Usage](./docs/XYZ_usage.md) ####
Rotate data from HEZ or HDZ to XYZ and back.

Extensive explanation of all input and output methods:
[IO Methods](readme_io.md)
