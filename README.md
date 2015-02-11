Geomag Algorithms
=================

Geomag algorithms includes tools to fetch, process, and output geomag data.


Install
-------

1. Install `python` (2.7.X)

    - On OS X, we recommend using Homebrew ( http://brew.sh/ )

2. Create a virtual environment (Optional, but recommended)

    `virtualenv geomagenv`
    activate virtual environment (note the period at the start).
    `. geomagenv/bin/activate`

3. Install numpy, obspy requires this be installed separately.

    `pip install numpy`

4. Install geomagio

    `pip install git+https://github.com/usgs/geomag-algorithms.git`

5. Use geomagio

    - Use the main scripts, `xyz.py -h`.
    - In python scripts, `import geomagio` or `import geomagio.iaga2002`.


Developing
----------

1. Install `node` and `python` (2.7.X)

    - On OS X, we recommend using Homebrew ( http://brew.sh/ )

2. Use npm to install `grunt-cli`

    `npm install -g grunt-cli`

3. Use pip to install `numpy`, `scipy`, `obspy`, and `flake8`

    `pip install numpy scipy obspy flake8`

4. Clone this project (or fork and clone your fork)

    `git checkout https://github.com/usgs/geomag-algorithms.git`

5. From root directory of project, install npm dependencies

    `npm install`

6. Run grunt to run unit tests, and watch for changes to python files

    `grunt`


Coding Standards
----------------

This project adheres to PEP8 standards in most cases:
    https://www.python.org/dev/peps/pep-0008

### PEP8 Exceptions

- Hanging/Visual indents (E126, E127, E128, E131)

    - line continuations should use two indentations (8 spaces).
    - do not use visual indents.
