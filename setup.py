from distutils.core import setup

setup(
    name='geomag-algorithms',
    version='0.0.0',
    description='USGS Geomag IO Library',
    url='https://github.com/usgs/geomag-algorithms',
    packages=[
        'geomagio',
        'geomagio.algorithm',
        'geomagio.iaga2002',
        'geomagio.imfv283',
        'geomagio.edge',
        'geomagio.pcdcp'
    ],
    install_requires=[
        'numpy',
        'matplotlib',
        'scipy',
        'obspy'
    ],
    scripts=[
        'bin/geomag.py'
    ]
)
