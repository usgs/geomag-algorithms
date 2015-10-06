"""Tests for MagWebFactory."""

from geomagio.iaga2002 import MagWebFactory
from nose.tools import assert_equals


def test_init():
    """iaga2002_test.MagWebFactory_test.test_init()

    Verify MagWebFactory calls parent constructor with MAGWEB_URL_TEMPLATE.
    """
    factory = MagWebFactory()
    assert_equals(factory.urlTemplate, MagWebFactory.MAGWEB_URL_TEMPLATE)
