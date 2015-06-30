
# XYZ Usage #

--xyz {geo, mag, obs, obsd} {geo, mag, obs, obsd}
'geo': ['X', 'Y', 'Z', 'F'],
'mag': ['H', 'D', 'Z', 'F'],
'obs': ['H', 'E', 'Z', 'F'],
'obsd': ['H', 'D', 'Z', 'F']

geomag.py --xyz geo geo
--observatory TUC
--starttime 2013-03-01T00:00:00Z --endtime 2013-03-31T23:59:00Z
--input-pcdcp-url file://data-pcdcp/./%(OBS)s%(year)s%(julian)s.%(i)s
--output-iaga-url file://data-iaga/./$(obs)s%(Y)s%(j)s.%(i)s
--type variation --interval minute
```

Background information with equations and implementation details:
[XYZ Background](XYZ.md)
