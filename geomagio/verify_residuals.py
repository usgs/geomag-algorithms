from residual import SpreadsheetAbsolutesFactory

saf = SpreadsheetAbsolutesFactory()

reading = saf.parse_spreadsheet(
    "/Users/pcain/Desktop/Residual Data/DED-20140952243.xlsm"
)

reading.update_absolutes()
