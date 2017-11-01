"""EDGE Location Code argument validation."""

import argparse
import re


def LocationCode(code):
    """EDGE Location Code argument validator.

    Location Code is the last component in a channel identifier;
    SNCL => Station, Network, Channel, Location Code

    Parameters
    ----------
    code : str
        the code to validate

    Returns
    -------
    str
        validated lcoation code.

    Raises
    ------
    argparse.ArgumentTypeError
        if the location code doesn't match the regular expression.
    """
    try:
        return re.match('^[A-Z0-9]{2}$', code).group(0)
    except AttributeError:
        raise argparse.ArgumentTypeError(
                'Invalid location code, expected /^[A-Z0-9]{2}$/')
