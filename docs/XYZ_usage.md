
# XYZ Usage #

`geomag.py --xyz {geo, mag, obs, obsd} {geo, mag, obs, obsd}`

### Reference Frames ###

There are 3 reference frames in this library.

#### Geographic or cartesian ####

 - `geo` is XYZ

 - 'geo':  ['X', 'Y', 'Z', 'F']

#### Magnetic or cylindrical ####

 - `mag` is HDZ

 - 'mag':  ['H', 'D', 'Z', 'F']

#### Observatory ####

 - `obs` is heZ

 - 'obs':  ['H', 'E', 'Z', 'F']
 - 'obsd': ['H', 'D', 'Z', 'F']

### Example ###

To convert HEZF data in pcdcp files to XYZF for Tucson observatory for all of
March 2013 output to iaga2002 files:

      geomag.py --xyz obs geo --observatory TUC --starttime 2013-03-01T00:00:00Z --endtime 2013-03-31T23:59:00Z --input-pcdcp-url file://data-pcdcp/./%(OBS)s%(year)s%(julian)s.%(i)s --output-iaga-url file://data-iaga/./$(obs)s%(Y)s%(j)s.%(i)s --type variation --interval minute


---
### Library Notes ###

> Note: Within this library all channels are uppercase.
> We use context (ie obs vs. mag vs geo), to differentiate between h,H; e,E;
> and d,D. This mirrors the various data formats, (ie IAGA2002, etc).

The underlying library provides calculations for both the basic conversions,
such as get_geo_y_from_mag, which is based off of Y = H sin(D), and higher
level conversions, such as get_geo_from_mag. (Which converts HD to XY).
These are provided by `geomagio.ChannelConverter`.

Upper libraries only provide higher level conversions, ie get_geo_from_mag.
This is the level most users should be accessing.
These are provided by `geomagio.StreamConverter`.

> Note: this library internally represents data gaps as NaN, and factories
> convert to this where possible.

---
### [Algorithm Theoretical Basis for "Geomag XYZ"](XYZ.md) ###
Describes the theory behind the XYZ algorithm, as well as some implementation
issues and solutions.
