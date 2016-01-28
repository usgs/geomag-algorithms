Development Dependencies
========================

These instructions only need to be completed if you plan on developing new
code for this project.

If developing on windows, see the [Windows](#windows) section below.

Begin Developing
----------------

1. Use npm to install `grunt-cli`

        npm install -g grunt-cli

2. Install `numpy`, `scipy`, `obspy`, and `flake8` if they aren't already
   installed.

3. Clone this project (or fork and clone your fork)

        git clone https://github.com/usgs/geomag-algorithms.git

4. From root directory of project, install npm dependencies

        npm install

5. Run grunt to run unit tests, and watch for changes to python files

        grunt


### Windows

1. Install the newest release of Node
   [(http://nodejs.org/download/)](http://nodejs.org/download/) for  Windows,
   using the Windows Installer (.msi).

1. Close and re-open your terminal so that your new PATH is loaded.


### Coding Standards

This project adheres to PEP8 standards in most cases:
    https://www.python.org/dev/peps/pep-0008

#### PEP8 Exceptions

- Hanging/Visual indents (E126, E127, E128, E131)

    - line continuations should use two indentations (8 spaces).
    - do not use visual indents.
