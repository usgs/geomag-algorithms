#! /usr/bin/env python

from os import path
import sys
# ensure geomag is on the path before importing
try:
    import geomagio  # noqa (tells linter to ignore this line.)
except:
    script_dir = path.dirname(path.abspath(__file__))
    sys.path.append(path.normpath(path.join(script_dir, '..')))


from geomagio.Controller import main, parse_args


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    main(args)
