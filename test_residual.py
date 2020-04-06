import json
from obspy import UTCDateTime

from geomagio.residual import (
    CalFileFactory,
    SpreadsheetAbsolutesFactory,
    WebAbsolutesFactory,
)


input_factory = SpreadsheetAbsolutesFactory()
readings = input_factory.get_readings(
    observatory="CMO",
    starttime=UTCDateTime(2020, 1, 1),
    endtime=UTCDateTime(2020, 1, 8),
)
print(
    json.dumps(
        readings,
        default=lambda x: isinstance(x, UTCDateTime) and str(x) or x.__dict__,
        indent=2,
    )
)

output_factory = CalFileFactory()
out = output_factory.format_readings(readings)
print(out)
