Solar Quiet and Disturbance Algorithm Usage
===========================================

The Solar Quiet and Disturbance Algorithm calculates `Solar Variation`,
`Solar Quiet` and `Disturbance` from raw Geomagnetic data.

`geomag.py --algorithm sqdist`


### Example

This example uses a state file to produce magnetic-h-based Dist, SQ, and SV
channels using the EDGE channel naming convention.

    bin/geomag.py \
      --input edge \
      --observatory BOU \
      --inchannels H E Z F \
      --starttime 2016-01-03T00:01:00 \
      --endtime 2016-01-04T00:00:00 \
      --algorithm sqdist \
      --sqdist-mag \
      --sqdist-statefile=/tmp/sqdist_h_state.json \
      --rename-output-channel H_SQ MSQ \
      --rename-output-channel H_SV MSV \
      --rename-output-channel H_Dist MDT \
      --outchannels MDT MSQ MSV \
      --output iaga2002 \
      --output-stdout

This example processes just one channel (X).

    bin/geomag.py \
      --input edge \
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
      --output iaga \
      --output-stdout

> Note only one inchannel is specified and the --sqdist-mag option is omitted.


### Library Notes

> Note: this library internally represents data gaps as NaN, and factories
> convert to this where possible.


### [Algorithm Theoretical Basis for "Geomag Solar Quiet and Disturbance"](SqDist.md) ###
Describes the theory behind the Solar Quiet and Disturbance algorithm, as
well as some implementation issues and solutions.
