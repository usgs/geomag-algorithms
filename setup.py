from distutils.core import setup

setup(
    name='geomag-algorithms',
    version='1.0.0',
    description='USGS Geomag IO Library',
    url='https://github.com/usgs/geomag-algorithms',
    packages=[
        'geomagio',
        'geomagio.algorithm',
        'geomagio.binlog',
        'geomagio.edge',
        'geomagio.iaga2002',
        'geomagio.imfjson',
        'geomagio.imfv122',
        'geomagio.imfv283',
        'geomagio.pcdcp',
        'geomagio.temperature',
        'geomagio.vbf'
    ],
    install_requires=[
        'numpy',
        'matplotlib',
        'scipy',
        'obspy',
        'pycurl'
    ],
    scripts=[
        'bin/geomag.py',
        'bin/geomag_webservice.py',
        'bin/make_cal.py'
    ]
)
