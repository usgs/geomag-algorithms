Edge/Earthworm IO Factory
=========================

Read from an Earthworm-style interface

`geomagio.edge.EdgeFactory`

## Command Line Example
(backslashes added for readability)
<pre>
geomag.py \
    <b>--input-edge cwbpub.cr.usgs.gov</b> \
    <b>--input-edge-port 2060</b> \
    --observatory BOU
    --inchannels H E Z F \
    --interval minute \
    --type variation \
    --starttime=2015-11-01T00:00:00Z \
    --endtime=2015-11-01T23:59:59Z \
    --output-iaga-stdout
</pre>


## API Example
```python
from __future__ import print_function
from geomagio.edge import EdgeFactory
from obspy.core import UTCDateTime

factory = EdgeFactory(host='cwbpub.cr.usgs.gov', port=2060)
data = factory.get_timeseries(
        observatory='BOU',
        channels=['H', 'E', 'Z', 'F'],
        interval='minute',
        type='variation',
        starttime=UTCDateTime('2015-11-01T00:00:00Z'),
        endtime=UTCDateTime('2015-11-01T23:59:59Z'))

print(data)
```

### Output
```
4 Trace(s) in Stream:
NT.BOU.R0.H | 2015-11-01T00:00:00.000000Z - 2015-11-02T00:00:00.000000Z | 60.0 s, 1441 samples
NT.BOU.R0.E | 2015-11-01T00:00:00.000000Z - 2015-11-02T00:00:00.000000Z | 60.0 s, 1441 samples
NT.BOU.R0.Z | 2015-11-01T00:00:00.000000Z - 2015-11-02T00:00:00.000000Z | 60.0 s, 1441 samples
NT.BOU.R0.F | 2015-11-01T00:00:00.000000Z - 2015-11-02T00:00:00.000000Z | 60.0 s, 1441 samples
```
