
# XYZ Usage #

geomag.py --xyz {geo, mag, obs, obsd} {geo, mag, obs, obsd}

  'geo':  ['X', 'Y', 'Z', 'F'],
  'mag':  ['H', 'D', 'Z', 'F'],
  'obs':  ['H', 'E', 'Z', 'F'],
  'obsd': ['H', 'D', 'Z', 'F']

### Example ###

To convert HEZF data in pcdcp files to XYZF for Tucson observatory for all of
March 2013 output to iaga2002 files:

      geomag.py --xyz obs geo --observatory TUC --starttime 2013-03-01T00:00:00Z --endtime 2013-03-31T23:59:00Z --input-pcdcp-url file://data-pcdcp/./%(OBS)s%(year)s%(julian)s.%(i)s --output-iaga-url file://data-iaga/./$(obs)s%(Y)s%(j)s.%(i)s --type variation --interval minute


### [Algorithm Theoretical Basis for "Geomag XYZ"](XYZ.md) ###
Describes the theory behind the XYZ algorithm, as well as some implementation
issues and solutions.
