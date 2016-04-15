Adjusted Algorithm Usage
========================

The Adjusted Algorithm transforms between `observatory`, and `geographic`,
channel orientations, using transform matrices derived from absolute and
baseline measurements.  Read more about the [Adjusted Algorithm](./Adjusted.md).

`geomag.py --algorithm sqdist`

### Example

This example uses a state file to produce magnetic-h-based Dist, SQ, and SV
channels using the EDGE channel naming convention.

    bin/geomag.py \
      --input-edge cwbpub.cr.usgs.gov \
      --observatory BOU \
      --inchannels H E Z F \
      --starttime 2016-01-03T00:01:00 \
      --endtime 2016-01-04T00:00:00 \
      --algorithm adjusted \
      --adjusted-statefile=/tmp/adjbou_state_.json \
      --outchannels MDT MSQ MSV \
      --output-iaga-stdout

This example processes just one channel (X).

    bin/geomag.py \
      --input-edge cwbpub.cr.usgs.gov \
      --observatory BOU \
      --inchannels X \
      --starttime 2016-01-03T00:01:00 \
      --endtime 2016-01-04T00:00:00 \
      --algorithm sqdist \
      --sqdist-statefile=/tmp/sqdist_x_state.json \
      --rename-output-channel X_Dist MXT \
      --rename-output-channel X_SQ MXQ \
      --rename-output-channel X_SV MXV \
      --outchannels MXT MXQ MXV \
      --output-iaga-stdout

> Note only one inchannel is specified and the --sqdist-mag option is omitted.


### Library Notes

> Note: this library internally represents data gaps as NaN, and factories
> convert to this where possible.
