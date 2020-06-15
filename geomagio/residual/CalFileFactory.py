"""Factory for CalFiles, used by MagProc.
"""
from __future__ import print_function

from typing import List
import itertools
from io import StringIO

from .Absolute import Absolute
from .Reading import Reading


class CalFileFactory(object):
    def format_readings(self, readings: List[Reading]) -> str:
        absolutes = []
        # list of all absolutes
        for r in readings:
            absolutes.extend(r.absolutes)
        return self._format_absolutes(absolutes)

    def _format_absolutes(self, absolutes: List[Absolute]) -> str:
        out = StringIO()
        # filter invalid
        absolutes = [a for a in absolutes if a.is_valid()]
        # sort by starttime
        absolutes = sorted(absolutes, key=lambda a: a.starttime)
        # group by date
        for date, cals in itertools.groupby(absolutes, key=lambda a: a.starttime.date):
            # convert group to list so it can be reused
            cals = list(cals)
            # within each day, order by H, then D, then Z
            for element in ["H", "D", "Z"]:
                element_cals = [c for c in cals if c.element == element]
                if not element_cals:
                    # no matching values
                    continue
                # channel header
                out.write(f"--{date:%Y %m %d} ({element})\n")
                for c in element_cals:
                    absolute, baseline = c.absolute, c.baseline
                    if element == "D":  # convert to minutes
                        absolute, baseline = absolute * 60, baseline * 60
                    out.write(  # this is one line...
                        f"{c.starttime.datetime:%H%M}-{c.endtime.datetime:%H%M}"
                        f" c{baseline:9.1f}{absolute:9.1f}\n"
                    )
        # add new line to end
        out.write("\n")
        return out.getvalue()

    def write_file(self, path: str, readings: List[Reading]):
        # generate string holding cal file's contents
        cal_str = self.format_readings(readings)
        with open(path, "wb") as f:
            f.write(cal_str)


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
