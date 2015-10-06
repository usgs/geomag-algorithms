#! /usr/bin/env python
from geomagio import Algorithm, Controller, TimeseriesFactory
from nose.tools import assert_is_instance


def test_controller():
    """Controller_test.test_controller()

  instantiate the controller, make certain the factories and algorithms
  are set
  """
    inputfactory = TimeseriesFactory()
    outputfactory = TimeseriesFactory()
    algorithm = Algorithm()
    controller = Controller(inputfactory, outputfactory, algorithm)
    assert_is_instance(controller._inputFactory, TimeseriesFactory)
    assert_is_instance(controller._outputFactory, TimeseriesFactory)
    assert_is_instance(controller._algorithm, Algorithm)
