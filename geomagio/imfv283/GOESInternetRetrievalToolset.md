Internet Retrieval of Satellite Data
====================================

### Data Retrieval Toolkit
Data retrieval uses the freely-available "OpenDCS Toolkit". OpenDCS is a
limited version of the licensed Sutron "DCS Toolkit". Information on
obtaining and using the tookit can be found here:
https://dcs1.noaa.gov/LRGS/LRGS-Client-Getting-Started.pdf

The non-open source documentation can be very useful, it can be found here:
http://lighthouse.tamucc.edu/dnrpub/Sutron/XPert/Software/ilex%20Software/DCS%20Tool%20Users%20Guide_4-4.pdf

### Accounts
You will need to set up an acount with NOAA (https://dcs1.noaa.gov/) to
retrieve Satellite data over the internet.

### getDcpMessages
getDcpMessage is a command line utility that fetches the asked for imfv283 data
from the server. You can also use the GUI to fetch it.

### The Search Criteria File
The file "Criteria.sc" contains the information used by getDcpMessages to
request data from the data server. It can be set up with a test editor,
or by using the opendcs GUI.
Example contents:

DAPS_SINCE: 2014/001 17:48
DAPS_UNTIL: now
NETWORKLIST: C:\networklists\DCPlist.NL
DAPS_STATUS: N
RETRANSMITTED: N
ASCENDING_TIME: true
RT_SETTLE_DELAY: true

### NETWORKLIST File
The networklist file, list the stations, and their related GOES code, that you
want to download for a given call to getdcpmessages.
The NETWORKLIST is the file ON THE GOES SERVER, not the local system.
Whatever name you used to upload it, including directory, will be the name on
the server. And it must be loaded to all servers you plan to use.
You can load it using either the opendcs gui, or by using the -N option for getDcpMessages.

### USGS ftp site.
The USGS stores a copy of the "OpenDCS Toolkit" and it's documentation at
the following ftp site. Use is strictly limited to the terms and prohibitions
as detailed at https://dcs1.noaa.gov

ftp://hazards.cr.usgs.gov/web/geomag-algorithms/
