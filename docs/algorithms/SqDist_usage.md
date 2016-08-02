Solar Quiet and Disturbance Algorithm Usage
===========================================

The Solar Quiet and Disturbance Algorithm calculates `Secular Variation`,
`Solar Quiet` and `Disturbance` from raw Geomagnetic data.

`geomag.py --algorithm sqdist`


### Examples

This example processes one Edge channel (X) for the BOU observatory, for one
day of minute data. The "memory" of SV is 30 days, or 43200 samples, so the
forgetting factor (--sqdist-alpha) is 1/43200, or ~2.315e-5. The initial
slope/trend of SV is assumed to be zero, and the --sqdist-beta option used here
ensures it will remain zero. The SQ signal repeats once-per-day, so the length
of the SQ vector (--sqdist-m) is 1440. SQ also has a memory of 30 days, but
because each element of SQ is updated only once-per-day, --sqdist-gamma must
be 1440 times larger than --sqdist-alpha. Finally, the outputs are renamed to
valid Edge channels, and written to standard output using IAGA2002 format.


    bin/geomag.py \
      --input edge \
      --observatory BOU \
      --inchannels X \
      --starttime 2016-01-03T00:01:00 \
      --endtime 2016-01-04T00:00:00 \
      --interval minute \
      --algorithm sqdist \
      --sqdist-alpha 2.315e-5 \
      --sqdist-beta 0 \
      --sqdist-m 1440 \
      --sqdist-gamma 3.333e-2 \
      --sqdist-statefile /tmp/sqdist_x_state.json \
      --rename-output-channel X_Dist MXT \
      --rename-output-channel X_SQ MXQ \
      --rename-output-channel X_SV MXV \
      --outchannels MXT MXQ MXV \
      --output iaga2002 \
      --output-stdout


This example decomposes the total horizontal field (--sqdist-mag) into SQ, SV,
and Dist. 1/minute data is assumed by default, so again SV has a memory of 43200
samples, or forgets 1/43200 (~2.315e-5) with each new observation processed
(--sqdist-alpha). By neglecting to specify --sqdist-beta, --sqdist-m, and
--sqdist-gamma, default values mean that no SQ correction is estimated (or more
precisely, SQ is zero). In other words, this is "simple exponential smoothing".

    bin/geomag.py \
      --input edge \
      --observatory BOU \
      --inchannels H E Z F \
      --starttime 2016-01-03T00:01:00 \
      --endtime 2016-01-04T00:00:00 \
      --algorithm sqdist \
      --sqdist-mag \
      --sqdist-alpha 2.315e-5 \
      --sqdist-statefile /tmp/sqdist_h_state.json \
      --rename-output-channel H_SQ MSQ \
      --rename-output-channel H_SV MSV \
      --rename-output-channel H_Dist MDT \
      --outchannels MDT MSQ MSV \
      --output iaga2002 \
      --output-stdout


### Library Notes

> Note: this library internally represents data gaps as NaN, and factories
> convert to this where possible.


### [Algorithm Theoretical Basis for "Geomag Solar Quiet and Disturbance"](SqDist.md) ###
Describes the theory behind the Solar Quiet and Disturbance algorithm, as
well as some implementation issues and solutions.
