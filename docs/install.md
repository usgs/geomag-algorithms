Installation
============

We recommend using virtual environments:
[(http://docs.python-guide.org/en/latest/dev/virtualenvs/)](http://docs.python-guide.org/en/latest/dev/virtualenvs/)

[Mac](#mac) and [Windows](#windows) specific details are below.

1. Install __geomagio__

       pip install git+https://github.com/usgs/geomag-algorithms.git

1. Use __geomagio__

  - Use the main script, `geomag.py -h`
  - In python scripts, `import geomagio`

The [Command Line Usage](./usage.md) and [Python API](./api.md)
pages have more instructions and examples.


---
### Mac ###

1. Install `python` (2.7.X)

   On OS X, we recommend using Homebrew [http://brew.sh/](http://brew.sh/)

1. Install numpy, obspy requires this be installed separately.

        pip install numpy

1. Install `node`, `git` and `python` (2.7.X).

   On OS X, we recommend using Homebrew
```
brew install node
brew install git
```

1. Use pip to install `numpy`, `scipy`, `obspy`, and `flake8`

        pip install numpy scipy obspy flake8

1. Update paths as needed in your `~/.bash_profile`:

        export PATH=$PATH:/usr/local/bin
        # npm installed binaries
        export PATH=$PATH:/usr/local/share/npm/bin
        # gem installed binaries
        export PATH=$PATH:/usr/local/opt/ruby/bin

1. Close and re-open your terminal so that your new PATH is loaded.
   Make sure to navigate back to your `geomag-algorithms` project directory.


---
### Windows ###

1. You will need a terminal tool for Windows. We recommend Git Bash
   [(http://git-scm.com/download/win)](http://git-scm.com/download/win), but
   another unix-like editor should work too.

1. Install Anaconda
   [(http://continuum.io/downloads)](http://continuum.io/downloads), which
   includes `numpy`, `scipy` and `flake8`.

1. Run `python` to verify that Anaconda's version of Python is being used.
   If it isn't, update your PATH so that Conda's HOME is before any other
   versions of Python.
