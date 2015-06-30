Readme dependencies

<a name="windows"></a>
### Windows ###

## Install ##
1. You will need a terminal tool for Windows. We used [Git Bash][] to test these
   steps, but [Cygwin][] or another unix-like editor should work fine too.

  - Choosing PATH environment: We recommend the __last option__ here to include
     Unix tools, but if you don't understand what that entails then use the
     _second option_ which still adds Git to your system PATH.
  - Besides that, all of the defaults should be sufficient.

1. Install [Anaconda][], which includes `numpy`, `scipy` and `flake8`.
  - We recommend using "Just Me" for the install to avoid potential admin
  issues.

1. Run `python` to verify that Anaconda's version of Python is being used.
   If it isn't, update your PATH so that Conda's HOME is before any other
   versions of Python.

1. Head back over to the main [install](README.md#install) and complete the
   instructions there.

## Develop ##

These instructions only need to be completed if you plan on developing new
code for this project.

1. Install the newest release of [Node][] for Windows, using the Windows
   Installer (.msi).
  - Use all of the defaults.

1. Close and re-open your terminal so that your new PATH is loaded.
   Make sure to navigate back to your `geomag-algorithms` project directory.

1. Install `obspy` from the terminal.

        easy_install obspy

[Git Bash]: http://git-scm.com/download/win
[Cygwin]: http://cygwin.com/install.html
[Node]: http://nodejs.org/download/
[Anaconda]: http://continuum.io/downloads

---
<a name="mac"></a>
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
<a name="ssh"></a>
### Add an SSH Key to GitHub ###

This only needs to be completed if you plan on developing and pushing new code
to this project.

  1. `ssh-keygen -t rsa -b 2048` (in terminal)
  2. Press **Enter** to accept the default save location.
  3. Enter a passphrase that you will remember.
  4. `cat ~/.ssh/id_rsa.pub`
     Copy the text block that is displayed.
     This is your SSH key.
     If you're on Window and can't copy the text from the terminal, go
     to `C:\Users\[your username here]\.ssh` and open the `id_rsa.pub` file
     with notepad.
  5. In GitHub, click **Edit Your Profile**.
  6. Select **SSH Keys** on the left.
  7. Click **Add SSH key**. Give it a meaningful title.
  8. Copy your SSH Key into the Key, and click **Add key**.
