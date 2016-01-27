Solar Quiet and Disturbance Algorithm Usage
===========================================

The Solar Quiet and Disturbance Algorithm calculates `Solar Variation`,
`Solar Quiet` and `Disturbance` from raw Geomagnetic data.

`geomag.py --algorithm sqdist`

> Note: this library internally represents data gaps as NaN, and factories
> convert to this where possible.


### [Algorithm Theoretical Basis for "Geomag Solar Quiet and Disturbance"](SqDist.md) ###
Describes the theory behind the Solar Quiet and Disturbance algorithm, as
well as some implementation issues and solutions.
