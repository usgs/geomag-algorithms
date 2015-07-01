Readme development dependencies

## Develop ##

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


---
### Windows ###

1. Install the newest release of [Node][] for Windows, using the Windows
   Installer (.msi).
  - All of the defaults should be sufficient.

1. Close and re-open your terminal so that your new PATH is loaded.

[Node]: http://nodejs.org/download/


---
### Coding Standards ###

This project adheres to PEP8 standards in most cases:
    https://www.python.org/dev/peps/pep-0008

### PEP8 Exceptions ###

- Hanging/Visual indents (E126, E127, E128, E131)

    - line continuations should use two indentations (8 spaces).
    - do not use visual indents.


---
### Add an SSH Key to GitHub ###

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

