"""Tests for IAGA2002Factory class"""

from nose.tools import assert_equals
from geomagio.iaga2002 import IAGA2002Factory


def test_parse_empty():
    """iaga2002_test.IAGA2002Parser_test.test_parse_empty()

    Verify the parse method returns an empty stream without exceptions
    if the data being parsed is empty.
    """
    parser = IAGA2002Factory()
    stream = parser.parse_string('')
    assert_equals(len(stream), 0)
