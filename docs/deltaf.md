# DeltaF Algorithm
Algorithm Theoretical Basis for "Geomag Delta F"

E. Joshua Rigler &lt;[erigler@usgs.gov](mailto:erigler@usgs.gov)&gt;

## Summary

Mathematical underpinnings and general algorithm considerations are presented
for estimating a so-called “Delta F” data stream. Delta F is the difference
between the magnetic vector magnitude measured at a given time, and a scalar
total-field measurement made by a nearby independent sensor at the same time.


## Background and Motivation

Magnetic vector measurements are typically made with fluxgate sensors capable
of capturing rapid variations along three orthogonal axes simultaneously.
However, the same technology that allows fast and accurate measurements of
magnetic field variation is generally more prone to erroneous measurements
than slower, more stable total-field sensors. "Delta F" is the difference
between the estimated total field, obtained from vector components, and the
measured total field. Delta F provides a useful time-dependent diagnostic for
magnetic observatory operators.

## Math and Theory

Delta F (∆F) is, conceptually, very simple:

- <a name="eq1"></a>Equation 1: '∆F = Fv - Fs'

...where Fs is the measured scalar total field, and  Fv is the estimated total
field obtained by adding vector components in quadrature (see figure for vector
component definitions):

- <a name="eq2"></a>Equation 2: 'Fv = X<sup>2</sup> + Y<sup>2</sup> + Z<sup>2</sup> = H<sup>2</sup> + Z<sup>2</sup> = h<sup>2</sup> + e<sup>2</sup> + Z<sup>2</sup>'

Of course, if data are only available in hdZ (where d=(D-D0)) coordinates, as
is common with USGS preliminary data, they should be converted into a Cartesian
system used in (2). See the [XYZ Algorithm](XYZ.md) for a discussion on the 
cartesian coordinate system used.

## Practical Considerations

### Non-synchronous Observations

Fluxgates and total-field sensors operate at different frequencies, with the
latter typically being the slower, more stable data source. While not an issue
for 1-minute data, the Intermagnet proposed 1-second standard states
“Compulsory full-scale scalar magnetometer  measurements with a data resolution
of 0.01 nT [are required] at a minimum sample period of 30 seconds”. First,
assume that the authors of this standard meant “maximum sample period of 30
seconds”. That said, this standard clearly allows scalar measurements to be
made less frequently than vector measurements. If this is indeed the case,
Delta F should correspond to the scalar measurement time steps, however is not
clearly stated in any found references which vector measurement should be used
to calculate Delta F.  The library requires all inputs use the same sampling rate.

### Missing Observations

The WG V-Dat modifications to the IAGA2002 data exchange format are very
specific about how to deal with “missing observations”. If Fs, or Fv and Fs are
missing, assign missing data flags/values to Delta F. If only Fv is missing,
set Delta F equal to -Fs.

## References

- IAGA WG V-DAT (2011), Addition to the IAGA2002 Data Exchange Format: Quasi
  Definitive (q) data type and valid geomagnetic element (G), IAGA WG V-DAT
  business meeting held during the IUGG-2011 Assembly in Mebourne, Austrailia,
  04 July 2011.
- St-Louis, B. (Ed.) (2012), INTERMAGNET Technical Reference Manual, Version 4.6,
  obtained
  from: http://www.intermagnet.org/publication-software/technicalsoft-eng.php
- Turbitt, C.; Matzka, J.; Rasson, J.; St-Louis, B.; and Stewart, D. (2013), An
  instrument performance and data quality standard for intermagnet one-second
  data exchange, IN: XVth IAGA Workshop on Geomagnetic Observatory Instruments
  and Data Processing, Cadiz, Spain, 4-14 June, 2012, p 186-188.
