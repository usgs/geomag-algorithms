## Command Line Usage

You can install the project if you haven't already with

      pip install git+https://github.com/usgs/geomag-algorithms.git

Running `geomag.py -h` or `geomag.py --help` will show an extensive list of
input parameters.

Some of the key parameters that should be specified are listed here along with
examples. They include

| Parameter                  | Format                                       |
| -------------------------- | -------------------------------------------- |
| __start time__             | YYYY-MM-DDTHH:MM:SSZ                         |
| __end time__               | YYYY-MM-DDTHH:MM:SSZ                         |
| __observatory code__       | 3-letter observatory code                    |
| __data input format __     | 'edge', 'iaga2002', 'pcdcp', ...             |
| __data input source__      | {--input, --input-file, ...}                 |
| __data output format__     | 'edge', 'iaga2002', 'pcdcp', ...             |
| __data output source__     | {--output-url, --output-file, ...}           |
| __input data channels__    | {[CHANNEL [CHANNEL ...]]}                    |
| __output data channels__   | {[CHANNEL [CHANNEL ...]]}                    |
| __data type__              | {variation, quasi-definitive, definitive}    |
| __interval__               | {minute, second, hour, day}                  |


### Examples ###

To retrieve all raw (**_variation_**) **_H_**, **_E_**, **_Z_** and **_F_**
**_minute_** data from Boulder Observatory (**_BOU_**) for the entire day of
**_July 1st 2014_** from an **_iaga2002_** formatted file and output
**_H_**, **_E_**, **_Z_** and **_F_** data to a **_pcdcp_** formatted file:

      geomag.py \
      --type variation \
      --inchannels H E Z F \
      --interval minute \
      --observatory BOU \
      --starttime 2014-07-01T00:00:00Z \
      --endtime 2014-07-01T23:59:00Z \
      --input iaga2002 \
      --input-file BOU20140701vmin.min \
      --outchannels H E Z F \
      --output pcdcp \
      --output-file BOU2014182.min

To retrieve all raw (**_variation_**) **_H_**, **_E_**, **_Z_** and **_F_**
**_minute_** data from Tucson Observatory (**_TUC_**) for the entire month of
**_March 2013_** from a group of **_pcdcp_** formatted files in a "data-pcdcp"
directory and output **_H_**, **_E_**, **_Z_** and **_F_** data to a group of
**_iaga2002_** formatted files in a "data-iaga" directory:

      geomag.py \
      --type variation \
      --inchannels H E Z F \
      --interval minute \
      --observatory TUC \
      --starttime 2013-03-01T00:00:00Z \
      --endtime 2013-03-31T23:59:00Z \
      --input pcdcp
      --input-url file://data-pcdcp/./%(OBS)s%(year)s%(julian)s.%(i)s \
      --output iaga2002
      --output-url file://data-iaga/./$(obs)s%(Y)s%(j)s.%(i)s \
      --outchannels H E Z F

To retrieve all **_Dst 4 minute_**, and **_Dst 3 minute_** data from **_USGS_**
for the entire day of **_Oct 1st 2015_** from an **_edge server_** (at
cwbpub.cr.usgs.gov) and output **_Dst 4 minute_**, and **_Dst 3 minute_**
data to an **_iaga2002_** formatted file:

      geomag.py \
      --type variation \
      --inchannels MGD MSD \
      --interval minute \
      --observatory USGS \
      --starttime 2015-10-01T00:00:00Z \
      --endtime 2015-10-01T23:59:00Z \
      --input edge
      --output iaga2002
      --output-stdout \
      --outchannels MGD MSD


---
### Algorithms ###

There are flags to specify certain algorithms should be run against the data.

#### XYZ ####

`--algorithm xyz`

`--xyz-from {geo, mag, obs, obsd}` (default is `obs`)

`--xyz-to {geo, mag, obs, obsd}` (default is `geo`)

#### [XYZ Usage](./algorithms/XYZ_usage.md) ####

Rotate data from HEZ (obs) or HDZ (mag) to XYZ (geo) and back.

Document: [/algorithms/XYZ_usage.md](./algorithms/XYZ_usage.md)

Extensive explanation of all input and output methods:
[IO Methods](./io.md)
