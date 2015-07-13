# DeltaF Usage #

`geomag.py --deltaf {geo, obs, obsd}`

### Reference Frames ###

There are 2 reference frames in this library.

#### Geographic or cartesian ####

 - `geo` is XYZ

 - 'geo':  ['X', 'Y', 'Z', 'F']

#### Observatory ####

 - `obs` is heZ

 - 'obs':  ['H', 'E', 'Z', 'F']
 - 'obsd': ['H', 'D', 'Z', 'F']

### Example ###

To convert HEZF data in pcdcp files to deltaf for Tucson observatory for all of
March 2013 output to edge:

      geomag.py --deltaf obs --observatory TUC \
      --starttime 2013-03-01T00:00:00Z --endtime 2013-03-31T23:59:00Z \
      --input-pcdcp-url file://data-pcdcp/./%(OBS)s%(year)s%(julian)s.%(i)s \
      --output-edge 127.0.0.1 \
      --type variation --interval minute --outchannels G

### Library Notes ###

> Note: Within this library all channels are uppercase.

> Note: this library internally represents data gaps as NaN, and factories
> convert to this where possible.

---
### [Algorithm Theoretical Basis for "Geomag Delta F"](DeltaF.md) ###
Describes the theory behind the Delta F algorithm, as well as some
implementation issues and solutions.
