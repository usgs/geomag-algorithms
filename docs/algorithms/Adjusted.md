Geomagnetic Adjusted Data
===========================================================

Abram Claycomb
&lt;[aclaycomb@usgs.gov](mailto:aclaycomb@usgs.gov)&gt;


## Background and Motivation

The magnetic field measured at an observatory of the USGS is
measured by a three-axis fluxgate sensor roughly aligned with the
magnetic field.  The three axes are:

- `h` - Horizontal 'leading' ahead of the local magnetic
declination (magnetic north) at the time of installation, so
that the local magnetic vector would eventually cross the h axis
- `e` - Horizontal, nominally orthogonal to h (roughly magnetic
  east)
- `z` - Nominally vertical, downward, and nominally orthogonal
to both `h` and `e`. Vertical at installation on a balancing
device with the intended purpose of staying level if the pier on
which it is mounted tilts under the sensor, all enclosed under a
glass dome to keep air movements from convecting heat directly
to the sensor from the room, or pushing the balanced system

Simultaneously, the field is measured by an Overhauser-effect
scalar magnetometer (non-directional).  This is called the total
field:

- `F` - Total field at the Overhauser pier

A third magnetometer, called a declination-inclination
magnetometer (DIM) is used to manually find direction of
the field for the purpose of calibrating the three-axis sensor
mentioned above, and converting the coordinate system to that of
a geographic north, east, and downward set of axes:

- `X` - Geographically North component of the magnetic field,
based on a survey of the absolute pier, and the azimuth mark, at
the time of installation, and periodically on a time scale of a
few years
- `Y` - Geographically East component of the magnetic field,
again based on the survey mentioned in `X` above
- `Z` - Vertical component of the magnetic field, downward,
 based on leveling the theodolite at each absolute measurement
 session

The declination and inclination measured by the DIM are:

- `D` - declination
- `I` - inclination

The measurements with the DIM are called absolutes and measured
on a timescale on the order of 1 week.  Four sets of four
measurements each are recorded on four orientations of the DIM
sensor and these measurements are averaged, to account for errors
in the sensor and its alignment to the optical axis of the
theodolite to which it is mounted.

The real-time measurements (to the nearest second) of `h`, `e`,
`z` and `F` are used to compute what are known as baselines, or
the differences in the pseudo-vector cylindrical coordinate
representation.  The equations relating these quantities, with
some definitions, are found below:

- `F_pier_correction` - measured on the order of once or twice
per year, by a second Overhauser recording for a few hours at
the absolute pier location (in place of the absolute DIM
  theodolite)
- `F_corrected = F + F_pier_correction`
- `X = F_corrected*cos(I)*cos(D)`
- `Y = F_corrected*cos(I)*sin(D)`
- `Z = F_corrected*sin(I)`
- `H_absolute = sqrt(X**2 + Y**2) = F_corrected*cos(I)`
- `D_absolute = arctan2(Y,X) = D`
- `Z_absolute = F_corrected*sin(I)`
- `H_ordinate = sqrt(h**2 + e**2)` - were the angles small, this may
have been historically approximated as `h`
- `D_ordinate = arctan2(e,h)` - were the angles small, this may
have been historically approximated as `e/h`
- `Z_ordinate = z`
- `H_baseline = H_absolute - H_ordinate`
- `D_baseline = D_absolute - D_ordinate`
- `Z_baseline = Z_absolute - Z_ordinate`

## Calibration to Reduce Errors and Transform Coordinates

The purpose of making the manual absolute measurements is to
account for errors in the vector magnetometer, and transform
the recorded `h`, `e`, `z` data into `X`, `Y`, `Z` coordinates.
There are several types of errors:

- non-orthogonal sensor error, which can be corrected by a
transformation matrix as a linear operator
- scale error: measurement by one unit in one sensor not being
   equal to one unit of the field, which can again be corrected
   by a different kind of transformation matrix; for fluxgate
   (and DIM) magnetic sensors, this is known to be
   temperature-dependent
- offset error: measurement with no field applied gives a
  non-zero sensor output; can be corrected by adding a vector,
  which can be re-cast as a matrix transformation and linear
  operator by an affine transformation; for fluxgate (and DIM)
  magnetic sensors, this is known to be temperature-dependent
- local magnetic disturbances - usually minimized by site
selection and disciplined operations during maintenance and
measurement.

The combined effect for the above mentioned errors, as well as
a final rotation to transform coordinates to X,Y,Z can be found
using a least-squares algorithm and baseline calculator data.  
This is phase one of the Adjusted Data project.


## Example

Usage for this algorithm is shown in this
[Adjusted Usage](Adjusted_usage.md)
example.

Example calculations of affine transformation matrices for USGS
observatories are shown in this
[Adjusted Example](AdjustedPhaseOneFunction2.ipynb) IPython
notebook.

There's a [Generation Tool](AdjustedPhase1GenerationTool.ipynb) notebook, for
generating the tranformation matrices in an automated fashion, with tools for
adjusting manually and previewing the effect on delta F, etc.


## References

 - Jankowski, J., and Sucksdorff, C., [Guide for Magnetic Measurements and Observatory Practice](http://www.iugg.org/IAGA/iaga-pages/pdf/Iaga-Guide-Observatories.pdf),
   Int. J. of Forecasting, 19(1), 143-148.

 - Hitchman, P. G., Crosthwaite, W. V., Lewis, A. M., and Wang, L. (2011), [Australian Geomagnetism Report 2011](https://d28rz98at9flks.cloudfront.net/73627/Rec2012_072.pdf)
