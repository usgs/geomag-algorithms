DeltaF Algorithm Usage
======================

Delta F is the difference between the magnitude of magnetic vector measurements,
and a scalar total-field measurement made by independent sensors.  Read more
about the [DeltaF Algorithm](./DeltaF.md).


`geomag.py --algorithm deltaf [--deltaf-from {geo, obs, obsd}]`


### Reference Frames

 - `geo`: `[X, Y, Z, F]`
 - `obs`: `[H, E, Z, F]`
 - `obsd`: `[H, D, Z, F]`


## Example

To compute DeltaF from  HEZF data for Tucson observatory:
```
geomag.py \
    --algorithm deltaf \
    --observatory TUC \
    --type variation \
    --interval minute \
    --inchannels H E Z F \
    --outchannels G \
    --starttime 2015-11-01T00:00:00Z \
    --endtime 2015-11-01T00:10:00Z \
    --input-edge cwbpub.cr.usgs.gov \
    --input-edge-port 2060 \
    --output-iaga-stdout
```


### Output
```
Format                 IAGA-2002                                    |
Source of Data         United States Geological Survey (USGS)       |
Station Name           Tucson                                       |
IAGA CODE              TUC                                          |
Geodetic Latitude      32.174                                       |
Geodetic Longitude     249.267                                      |
Elevation              946                                          |
Reported               GNULNULNUL                                   |
Sensor Orientation     HDZF                                         |
Digital Sampling       100.0 second                                 |
Data Interval Type     filtered 1-minute (00:15-01:45)              |
Data Type              variation                                    |
# DECBAS               7258    (Baseline declination value in       |
# tenths of minutes East (0-216,000)).                              |
# Vector 1-minute values are computed from 1-second values using    |
# the INTERMAGNET gaussian filter centered on the minute. Scalar    |
# 1-minute values are computed from 1-second values using the       |
# INTERMAGNET gaussian filter centered on the minute.               |
# CONDITIONS OF USE: The Conditions of Use for data provided        |
# through INTERMAGNET and acknowledgement templates can be found at |
# www.intermagnet.org                                               |
DATE       TIME         DOY     TUCG      TUCNUL    TUCNUL    TUCNUL |
2015-11-01 00:00:00.000 305      -174.39  99999.99  99999.99  99999.99
2015-11-01 00:01:00.000 305      -174.40  99999.99  99999.99  99999.99
2015-11-01 00:02:00.000 305      -174.40  99999.99  99999.99  99999.99
2015-11-01 00:03:00.000 305      -174.39  99999.99  99999.99  99999.99
2015-11-01 00:04:00.000 305      -174.39  99999.99  99999.99  99999.99
2015-11-01 00:05:00.000 305      -174.41  99999.99  99999.99  99999.99
2015-11-01 00:06:00.000 305      -174.39  99999.99  99999.99  99999.99
2015-11-01 00:07:00.000 305      -174.34  99999.99  99999.99  99999.99
2015-11-01 00:08:00.000 305      -174.39  99999.99  99999.99  99999.99
2015-11-01 00:09:00.000 305      -174.39  99999.99  99999.99  99999.99
2015-11-01 00:10:00.000 305      -174.39  99999.99  99999.99  99999.99
```
