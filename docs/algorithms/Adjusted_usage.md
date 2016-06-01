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


### Statefile Example Content

This is the content of /etc/adjusted/adjbou_state_.json:

{"M32": -0.011809351484171948, "M41": -0.0, "M44": 1.0, "PC": -22,
 "M24": -0.84581925813504188, "M43": 0.0,
 "M34": 905.38008857968441, "M33": 0.99618690124939757,
 "M21": 0.16680172992706568, "M22": 0.98791620101212796,
 "M23": -0.0049868332295851525, "M11": 0.98342757670906167,
 "M42": -0.0, "M13": 0.027384986324932026,
 "M12": -0.15473074200902157, "M14": -1276.1646811919759,
 "M31": -0.006725053082782385}

### Library Notes

> Note: this library internally represents data gaps as NaN, and
factories
> convert to this where possible.
