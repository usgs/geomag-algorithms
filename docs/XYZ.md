
# Algorithm Theoretical Basis for "Geomag XYZ"

E. Joshua Rigler &lt;[erigler@usgs.gov](mailto:erigler@usgs.gov)&gt;


# Summary

Mathematical underpinnings and general algorithm considerations are presented
for converting geomagnetic observations from so-called HEZ coordinates, used by
the USGS geomagnetism program, into XYZ coordinates, used by a growing number
of international geomagnetism programs, as well as various academic and
commercial entities. Inverse transformations are also provided.


# Background and Motivation

Historically, the most common coordinate system used to specify measured
geomagnetic fields has been HDZ, where:

- `H` is the magnitude of the geomagnetic field vector tangential to the Earth's surface;
- `D` is the declination, or clockwise angle from the vector pointing to the geographic north pole to the H vector;
- `Z` is the downward component of the geomagnetic field.

> Note: this library internally refers to the `HDZ` coordinate system as "mag",
> short for magnetic/cylindrical.

This coordinate system is useful for navigation (it is the natural coordinate
system for a magnetic compass), and any scientific analysis conducted in a
geomagnetic field-aligned reference frame, but is somewhat awkward for most
other applications.

A more generally useful set of coordinates for scientific
analysis and engineering applications is the XYZ system:

-  `X` is the magnitude of the geographic north pole component of the H vector;
-  `Y` is the magnitude of the east component of the H vector;
-  `Z` is the downward component of the geomagnetic field, same as before.

> Note: this library internally refers to the `XYZ` coordinate system as "geo",
> short for geographic/cartesian.

Conversion between these two coordinate systems involves relatively straight-
forward trigonometry (see Eqs. [1](#eq1), [2](#eq2), and [3](#eq3)).

However, in practice, a 3-axis
magnetometer necessarily takes on a fixed orientation upon installation. For
USGS observatories, this is aligned with the average magnetic north vector and
downward, with the final axis completes a right-handed 3-dimensional coordinate
system (roughly eastward). This is often referred to as HEZ coordinates, but
for the remainder of this document we will refer to it as heZ, to avoid
confusion with more traditional definitions of H and E(==Y).

> Note: this library internally refers to the `heZ` coordinate system as "obs",
> short for observatory.

The purpose of this document then is to provide a mathematical and algorithmic
description of how one converts data measured in heZ coordinates to true HDZ,
and finally to XYZ.


# Math and Theory

First, following definitions in the previous section, the conversion from
cylindrical HDZ to Cartesian XYZ is very straight-forward trigonometry:

- <a name="eq1"></a>Equation 1: `X = H cos(D)`
- <a name="eq2"></a>Equation 2: `Y = H sin(D)`
- <a name="eq3"></a>Equation 3: `Z = Z`

However, as noted previously, the USGS aligns its magnetometers with the
magnetic north upon installation at an observatory, meaning raw data is
generated in heZ coordinates, where "h" is is the primary axis in a fixed
reference frame, "e" is the secondary axis in this reference frame, and "Z" is
the tertiary axis, which remains common for all reference frames discussed in
this document.

![Magnetic Field Vectors in three coordinate systems](images/figure.png)

The figure above illustrates how the same full magnetic field vector **F**, can
be represented in heZ, HDZ, and XYZ coordinates. Red objects are specific to
the magnetometer's reference frame, while blue objects are specific to the
geographic reference frame. Black is common to all frames considered here, and
dashed lines help define Cartesian grids.

One thing that is not labeled in this figure is the angle d (see [Eq. 4](#eq4)),
which is the difference between declination D, and a declination
baseline (D0, or DECBAS).

The equations Eqs [4](#eq4), [5](#eq5), [6](#eq6) describe how to convert the
horizontal components of a USGS magnetometer's raw data element into more
standard H and D components.

- <a name="eq4"></a>Equation 4: `d = arctan(e/h)`
- <a name="eq5"></a>Equation 5: `D = D0 + d`
- <a name="eq6"></a>Equation 6: `H = sqrt(h*h + e*e) = h / cos(d)`

To inverse transform from `XY` to `HD`:

- <a name="eq7"></a>Equation 7: `H = sqrt(X*X + Y*Y)`
- <a name="eq8"></a>Equation 8: `D = arctan(Y/X)`

...and from `HD` to `he`:

- <a name="eq9"></a>Equation  9: `d = D - D0`
- <a name="eq10"></a>Equation 10: `h = sqrt(H*H / (1 + tan(d)*tan(d))) = H cos(d)`
- <a name="eq11"></a>Equation 11: `e = h * tan(d)`

It is worth noting that there is potential for mathematically undefined results
in several of the preceding equations, where infinite ratios are a possible
argument to the arctan() function. However, Python's Numpy package, and indeed
most modern math libraries, will return reasonable answers in such situations
(hint: arctan(Inf)==pi/2).

> Note: this library uses the atan2 function to handle the noted problem of
> infinite ratios.


# Practical Considerations

## Magnetic Intensity Units

It is understood that all raw data inputs are provided in units of nanoTesla
(nT). Of course this is not required for the equations to be valid, but it is
incumbent on the programmer to make sure all input data units are the same, and
that output units are defined accurately.

## Declination Angular Units

The equations in the preceding section are relatively simple to code up, with
the standard caveat that angles must be appropriate for the trigonometric
functions (e.g., if sin/cos/tan expect radians, be sure to provide parameters
in radians). One thing that can potentially complicate this is that IAGA
standards require declination angles to be in minutes of arc. Furthermore, D0
(DECBAS) is not very well-defined by IAGA standards, but is typically reported
in tenths of minutes of arc. None of these are difficult to convert, but it is
incumbent on the programmer to make sure they know what units are being used
for the inputs.

> Note: this library internally uses radians for all angles, and factories
> convert to and from this standard.

## Declination Baseline

Declination baseline is not well-defined by IAGA standards. The typical method
used to publish it with actual data is to include it in the metadata. For older
IMF formatted files, it is part of the periodic block header. For IAGA2002
formatted file, it may be in the file header, but is not required. To the
best of my knowledge, if it is not included, one should assume it is zero, but
no corroborating documentation could be found to justify this statement.

> Note: this library makes declination baseline available in trace stats as
> `declination_base` ([see all trace metadata](./metadata.md).  The IAGA Factory
> also attempts to parse DECBAS from the comments section.


## Declination in USGS Variations Data

The USGS variations data is actually published in hdZ coordinates. If one
wishes to apply equations in the preceding section to USGS variations data,
they must first convert "d" back into "e" via Eq. [11](#eq11).

## Data Flags

It should go without saying that bad data in one coordinate system is bad data
in another. However, on occasion, operational USGS Geomagnetism Program code has
been discovered where coordinate transformations were applied
before checking data flags. This is not an issue if data flags are NaN
(not-a-number values), but more typical for Geomag data, these are values like
99999, which can lead to seemingly valid, but erroneous values at times when the
raw data were known to be bad.

> Note: this library internally represents data gaps as NaN, and factories convert
> to this where possible.


# Algorithm

The geomag algorithm references the 3 reference frames as geo for
geographic/cartesian, obs for observatory and mag for magnetic/cylindrical. In
reference to this article

- `geo` is XYZ
- `obs` is heZ
- `mag` is HDZ

> Note: in this library all channels are uppercase.
> We use context (ie obs vs. mag), to differentiate between h,e and HD.
> This mirrors the various data formats, (ie IAGA2002, etc).

The underlying library provides calculations for both the basic conversions,
such as get_get_y_from_mag, which is based off of Y = H sin(D), and higher
level conversions, such as get_geo_from_mag. (Which converts HD to XY).
These are provided by `geomagio.ChannelConverter`.

Upper libraries only provide higher level conversions, ie get_geo_from_mag.
This is the level most users should be accessing.
These are provided by `geomagio.StreamConverter`.
