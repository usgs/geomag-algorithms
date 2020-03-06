# Development Dependencies

These instructions only need to be completed if you plan on developing new
code for this project, but may also be used to run a local copy of the code.

## Clone Project

This project uses a forking workflow.
https://guides.github.com/activities/forking/

1.  Fork this project on Github.

    https://github.com/usgs/geomag-algorithms.git

2.  Clone your fork

        git clone https://github.com/{YOUR_GITHUB_ACCOUNT}/geomag-algorithms.git
        cd geomag-algorithms
        git remote add upstream https://github.com/usgs/geomag-algorithms.git

3.  Use branches to develop new features and submit pull requests.

## Install Dependencies

- Using `pipenv`
  https://pipenv.kennethreitz.org/en/latest/

  > `pyenv` is also useful for installing specific/multiple versions of python
  >
  > - https://github.com/pyenv/pyenv
  > - https://github.com/pyenv-win/pyenv-win

      pipenv install --dev
      pipenv shell

- Or, using Miniconda/Anaconda
  https://conda.io/miniconda.html

      conda config --add channels conda-forge
      conda create --name geomagenv obspy pycurl black pre-commit pytest pytest-cov webtest
      conda activate geomagenv

## Coding Standards

This project uses _The Black Code Style_
https://black.readthedocs.io/en/stable/the_black_code_style.html

## Developer Tools

- **Code Formatting**

  This project uses the `black` formatter, combined with `pre-commit`, to
  automatically format code before it is committed.

  VSCode ( https://code.visualstudio.com/ ), with the `Python` extension,
  can be configured to automatically format using `black` when files are saved.
  The `Formatting Toggle` extension is also useful.

  You can also manually format all files in the project by running

      black .

- **Unit tests**

  Run unit tests using PyTest

      pytest

- **Unit test coverage**

      pytest --cov=geomagio

## Routine Git Updates

- **Pulling new changes**

  When starting a new branch, or before putting in a pull request, make sure
  you have the latest changes from the `upstream` repository.

  > The local master branch should only be used for synchonization with the
  > `upstream` repository, and we recommend always using the `--ff-only` option.

      git checkout master
      git pull --ff-only upstream master

- **Rebase an existing branch**

  After downloading updates into the master branch, feature branches need to be
  rebased so they include any already merged changes.

      git checkout FEATURE-BRANCH
      git rebase master

  Resolve any rebase conflicts.
  If you have already pushed this branch to your fork, you may need to force push
  because branch history has changed.
