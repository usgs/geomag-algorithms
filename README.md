Geomag Algorithms
=================

Geomag algorithms includes tools to fetch, process, and output geomag data.


Dependencies
------------

1. Install `node` and `python` (2.7.X)

    - On OS X, we recommend using Homebrew ( http://brew.sh/ )

2. Use npm to install `grunt-cli`

    `npm install -g grunt-cli`

3. Use pip to install `numpy`, `scipy`, `obspy`, and `flake8`

    `pip install numpy scipy obspy flake8`


Developing
----------

1. Install the dependencies

2. Clone this project (or fork and clone your fork)

    `git checkout https://github.com/usgs/geomag-algorithms.git`

3. From root directory of project, install npm dependencies

    `npm install`

4. Run grunt to run unit tests, and watch for changes to python files

    `grunt`


Coding Standards
----------------

This project adheres to PEP8 standards in most cases:
    https://www.python.org/dev/peps/pep-0008

### PEP8 Exceptions

- Hanging indents (E126)

    line continuations should use two indentations (8 spaces).
