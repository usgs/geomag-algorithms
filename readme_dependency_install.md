Readme install dependencies

## Install ##

We recommend using [virtual environments][].

Check out the [Mac](#mac) and [Windows](#windows) details below for more
specific dependency information.

1. Install __geomagio__

        pip install git+https://github.com/usgs/geomag-algorithms.git

1. Use __geomagio__

  - Use the main script, `geomag.py -h`
  - In python scripts, `import geomagio`

The [Usage](readme_usage.md) page has more detailed instructions and examples.

[virtual environments]: http://docs.python-guide.org/en/latest/dev/virtualenvs/


---
### Mac ###

1. Install `python` (2.7.X)

        On OS X, we recommend using Homebrew ( http://brew.sh/ )

1. Install numpy, obspy requires this be installed separately.

        pip install numpy

1. Install `node`, `git` and `python` (2.7.X).
   On OS X, we recommend using [Homebrew][]

        brew install node
        brew install git

1. Use pip to install `numpy`, `scipy`, `obspy`, and `flake8`

        pip install numpy scipy obspy flake8

1. Update paths as needed in your `~/.bash_profile`:

        export PATH=$PATH:/usr/local/bin`
        # npm installed binaries
        export PATH=$PATH:/usr/local/share/npm/bin
        # gem installed binaries
        export PATH=$PATH:/usr/local/opt/ruby/bin

1. Close and re-open your terminal so that your new PATH is loaded.
   Make sure to navigate back to your `geomag-algorithms` project directory.

[Homebrew]: http://brew.sh/

---
### Windows ###

1. You will need a terminal tool for Windows. [Git Bash][] was used to test
   these steps, but [Cygwin][] or another unix-like editor should work too.

  - Choosing PATH environment: We recommend the __last option__ here to include
     Unix tools, but if you don't understand what that entails then use the
     _second option_ which still adds Git to your system PATH.
  - Besides that, all of the defaults should be sufficient.

1. Install [Anaconda][], which includes `numpy`, `scipy` and `flake8`.
  - We recommend using _"Just Me"_ for the install to avoid potential admin
  issues.

1. Run `python` to verify that Anaconda's version of Python is being used.
   If it isn't, update your PATH so that Conda's HOME is before any other
   versions of Python.

[Git Bash]: http://git-scm.com/download/win
[Cygwin]: http://cygwin.com/install.html
[Anaconda]: http://continuum.io/downloads
