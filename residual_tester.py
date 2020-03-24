import openpyxl
from geomagio.residual import SpreadsheetAbsolutesFactory, Reading


path = "DED-USGS-20140300306.xlsm"
saf = SpreadsheetAbsolutesFactory()
workbook = openpyxl.load_workbook(path, data_only=True)
constants_sheet = workbook["constants"]
measurement_sheet = workbook["measurement"]
summary_sheet = workbook["Summary"]
metadata = saf._parse_metadata(constants_sheet, measurement_sheet, summary_sheet)
include_measurements = True
absolutes = saf._parse_absolutes(summary_sheet, metadata["date"])
measurements = (
    include_measurements
    and saf._parse_measurements(measurement_sheet, metadata["date"])
    or None
)

ordinates = (
    include_measurements
    and saf._gather_ordinates(measurement_sheet, metadata["date"], metadata["station"])
    or None
)

reading = Reading(
    absolutes=absolutes,
    azimuth=metadata["mark_azimuth"],
    hemisphere=metadata["hemisphere"],
    measurements=measurements,
    metadata=metadata,
    pier_correction=metadata["pier_correction"],
    ordinates=ordinates,
)

res = reading.calculate()

for i in res[0][:-1]:
    print("**************")
    print("element", i.element)
    print("baseline", i.baseline)
    print("absolute", i.absolute)
print("**************")
print("scale", res[1])
