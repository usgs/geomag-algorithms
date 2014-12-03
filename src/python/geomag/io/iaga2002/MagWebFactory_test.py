"""Tests for MagWebFactory."""

import MagWebFactory
from nose.tools import assert_equals


def test_init():
    """geomag.io.iaga2002.MagWebFactory_test.test_init()

    Verify MagWebFactory calls parent constructor with MAGWEB_URL_TEMPLATE.
    """
    factory = MagWebFactory.MagWebFactory()
    assert_equals(factory.urlTemplate, MagWebFactory.MAGWEB_URL_TEMPLATE)

