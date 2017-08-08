Average Algorithm Usage
========================

The average algorithm takes data streams from multiple observatories
over one channel and returns a single averaged data stream.


### Example
To compute the average of H over the observatories of HON and SJG

```
geomag.py \
    --algorithm average \
    --observatory HON SJG GUA \
    --type variation \
    --interval minute \
    --inchannels H \
    --outchannels H \
    --starttime 2017-07-04T00:00:00Z \
    --endtime 2017-07-04T00:10:00Z \
    --input edge \
    --output iaga2002 \
    --output-stdout
```

### Output

```
 Format                 IAGA-2002                                    |
 Source of Data         United States Geological Survey (USGS)       |
 Station Name           USGS                                         |
 IAGA CODE              USGS                                         |
 Geodetic Latitude      40.137                                       |
 Geodetic Longitude     254.764                                      |
 Elevation              1682                                         |
 Reported               HNULNULNUL                                   |
 Sensor Orientation     HDZF                                         |
 Digital Sampling       100.0 second                                 |
 Data Interval Type     1-minute calculated                          |
 Data Type              variation                                    |
 # DECBAS               0       (Baseline declination value in       |
 # tenths of minutes East (0-216,000)).                              |
 # CONDITIONS OF USE: The Conditions of Use for data provided        |
 # through INTERMAGNET and acknowledgement templates can be found at |
 # www.intermagnet.org                                               |
DATE       TIME         DOY     USGSH     USGSNUL   USGSNUL   USGSNUL|
2017-07-04 00:00:00.000 185     29854.29  99999.00  99999.00  99999.00
2017-07-04 00:01:00.000 185     29854.31  99999.00  99999.00  99999.00
2017-07-04 00:02:00.000 185     29854.28  99999.00  99999.00  99999.00
2017-07-04 00:03:00.000 185     29854.18  99999.00  99999.00  99999.00
2017-07-04 00:04:00.000 185     29854.15  99999.00  99999.00  99999.00
2017-07-04 00:05:00.000 185     29854.20  99999.00  99999.00  99999.00
2017-07-04 00:06:00.000 185     29854.22  99999.00  99999.00  99999.00
2017-07-04 00:07:00.000 185     29854.35  99999.00  99999.00  99999.00
2017-07-04 00:08:00.000 185     29854.52  99999.00  99999.00  99999.00
2017-07-04 00:09:00.000 185     29854.69  99999.00  99999.00  99999.00
2017-07-04 00:10:00.000 185     29854.76  99999.00  99999.00  99999.00
```
