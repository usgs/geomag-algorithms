"""
Load IAGA2002 format files from http://magweb.cr.usgs.gov
"""

from IAGA2002Factory import IAGA2002Factory, IAGA_FILE_PATTERN


# url pattern for magweb.cr.usgs.gov
MAGWEB_URL_TEMPLATE = 'http://magweb.cr.usgs.gov/data/magnetometer/' + \
    '%(OBS)s/%(interval)s%(type)s/' + IAGA_FILE_PATTERN


class MagWebFactory(IAGA2002Factory):
    """IAGA2002Factory configured for magweb.cr.usgs.gov"""

    def __init__(self):
        """Create a IAGA2002Factory configured to use magweb.cr.usgs.gov"""
        IAGA2002Factory.__init__(self, MAGWEB_URL_TEMPLATE)
