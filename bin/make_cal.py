#! /usr/bin/env python

"""
Usage:
    python make_cal.py OBSERVATORY YEAR
"""
from __future__ import print_function

from datetime import datetime
import itertools
import json
import os
import sys
import urllib2


############################################################################
# CONFIGURATION

# format used to output files
# "{OBSERVATORY}" and "{YEAR}" are replaced with argument values
FILENAME_FORMAT = "./{OBSERVATORY}{YEAR}WebAbsMaster.cal"

# url for observation web service
SERVICE_URL = "https://geomag.usgs.gov/baselines/observation.json.php"

############################################################################
# DO NOT EDIT BELOW THIS LINE


# parse observatory and year arguments
if len(sys.argv) != 3:
    cmd = sys.argv[0]
    print("Usage:   {} OBSERVATORY YEAR".format(cmd), file=sys.stderr)
    print("Example: {} BOU 2016".format(cmd), file=sys.stderr)
    sys.exit(1)

OBSERVATORY = sys.argv[1]
YEAR = int(sys.argv[2])


# request observations from service
url = (
    SERVICE_URL
    + "?"
    + "&".join(
        [
            "observatory=" + OBSERVATORY,
            "starttime=" + str(YEAR) + "-01-01",
            "endtime=" + str(YEAR + 1) + "-01-01",
        ]
    )
)

try:
    print("Loading data from web service\n\t{}".format(url), file=sys.stderr)
    response = urllib2.urlopen(
        url,
        # allow environment certificate bundle override
        cafile=os.environ.get("SSL_CERT_FILE"),
    )
    data = response.read()
    observations = json.loads(data)
except Exception as e:
    print("Error loading data ({})".format(str(e)), file=sys.stderr)
    sys.exit(1)


# extract all valid cal values
cals = []
for observation in observations["data"]:
    for reading in observation["readings"]:
        for channel in ["H", "D", "Z"]:
            cal = reading[channel]
            if (
                not cal["absolute"]
                or not cal["baseline"]
                or not cal["end"]
                or not cal["start"]
                or not cal["valid"]
            ):
                # not a valid cal value
                continue
            # convert D values from degrees to minutes
            multiplier = 60 if channel == "D" else 1
            absolute = cal["absolute"] * multiplier
            baseline = cal["baseline"] * multiplier
            end = datetime.utcfromtimestamp(cal["end"])
            start = datetime.utcfromtimestamp(cal["start"])
            cals.append(
                {
                    "absolute": absolute,
                    "baseline": baseline,
                    "channel": channel,
                    "end": end,
                    "start": start,
                }
            )


# format calfile
CAL_HEADER_FORMAT = "--{date:%Y %m %d} ({channel})"
CAL_LINE_FORMAT = "{start:%H%M}-{end:%H%M} c{baseline:9.1f}{absolute:9.1f}"

calfile = []
# output by date in order
cals = sorted(cals, key=lambda c: c["start"])
# group by date
for date, cals in itertools.groupby(cals, key=lambda c: c["start"].date()):
    # convert group to list so it can be reused
    cals = list(cals)
    # within each day, order by H, then D, then Z
    for channel in ["H", "D", "Z"]:
        channel_cals = [c for c in cals if c["channel"] == channel]
        if not channel_cals:
            # no matching values
            continue
        # add channel header
        calfile.append(CAL_HEADER_FORMAT.format(channel=channel, date=date))
        calfile.extend([CAL_LINE_FORMAT.format(**c) for c in channel_cals])
calfile.append("")


# write calfile
filename = FILENAME_FORMAT.format(OBSERVATORY=OBSERVATORY, YEAR=YEAR)
print("Writing cal file to {}".format(filename), file=sys.stderr)
with open(filename, "wb", -1) as f:
    f.write(os.linesep.join(calfile))


"""
CAL format example:
- ordered by date
- within date, order by H, then D, then Z component
- component values order by start time
- D component values in minutes.


--2015 03 30 (H)
2140-2143 c    175.0  12531.3
2152-2156 c    174.9  12533.3
2205-2210 c    174.8  12533.1
2220-2223 c    174.9  12520.7
--2015 03 30 (D)
2133-2137 c   1128.3   1118.5
2145-2149 c   1128.4   1116.4
2159-2203 c   1128.3   1113.1
2212-2216 c   1128.4   1113.5
--2015 03 30 (Z)
2140-2143 c    -52.9  55403.4
2152-2156 c    -52.8  55403.8
2205-2210 c    -52.8  55404.0
2220-2223 c    -52.8  55410.5
--2015 07 27 (H)
2146-2151 c    173.5  12542.5
2204-2210 c    173.8  12542.5
2225-2229 c    173.8  12547.2
2240-2246 c    173.6  12538.7
--2015 07 27 (D)
2137-2142 c   1127.8   1109.2
2154-2158 c   1128.3   1106.3
2213-2220 c   1128.0   1106.3
2232-2237 c   1128.3   1104.7
--2015 07 27 (Z)
2146-2151 c    -53.9  55382.7
2204-2210 c    -54.0  55382.5
2225-2229 c    -54.1  55383.7
2240-2246 c    -54.1  55389.0
"""
