# DeltaF Usage #

`geomag.py --deltaf {geo, obs, obsd}`

### Reference Frames ###
 - 'geo':  ['X', 'Y', 'Z', 'F']
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

Please see the Library Notes for [XYZ Usage](./XYZ_usage.md)

---
### [DeltaF Algorithm](DeltaF.md) ###
Describes the theory behind the Delta F algorithm, as well as some
implementation issues and solutions.
