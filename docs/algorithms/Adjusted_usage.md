Adjusted Algorithm Usage
========================

The Adjusted Algorithm transforms between `observatory`, and
`geographic`, channel orientations, using transform matrices
derived from absolute and baseline measurements.  Read more about
the [Adjusted Algorithm](./Adjusted.md).

`geomag.py --algorithm sqdist`

### Example

This example uses a state file to produce X, Y, Z and F channels
from raw H, E, Z and F channels using the EDGE channel naming
convention.  Absolutes were used to compute a transform matrix
contained in the statefile.  The pier correction is also currently
contained in the statefile.

    bin/geomag.py \
      --input-edge cwbpub.cr.usgs.gov \
      --observatory BOU \
      --inchannels H E Z F \
      --starttime 2016-01-03T00:00:00 \
      --endtime 2016-01-03T23:59:59 \
      --algorithm adjusted \
      --adjusted-statefile=/etc/adjusted/adjbou_state_.json \
      --outchannels X Y Z F \
      --output-iaga-stdout


### Library Notes

> Note: this library internally represents data gaps as NaN, and
factories
> convert to this where possible.
