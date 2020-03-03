#! /usr/bin/env python

from __future__ import absolute_import, print_function

import os
import sys
from wsgiref.simple_server import make_server

# ensure geomag is on the path before importing
try:
    import geomagio  # noqa (tells linter to ignore this line.)
except ImportError:
    path = os.path
    script_dir = path.dirname(path.abspath(__file__))
    sys.path.append(path.normpath(path.join(script_dir, "..")))
    import geomagio


if __name__ == "__main__":
    # read configuration from environment
    edge_host = os.getenv("EDGE_HOST", "cwbpub.cr.usgs.gov")
    edge_port = int(os.getenv("EDGE_PORT", "2060"))
    factory_type = os.getenv("GEOMAG_FACTORY_TYPE", "edge")
    webservice_host = os.getenv("GEOMAG_WEBSERVICE_HOST", "")
    webservice_port = int(os.getenv("GEOMAG_WEBSERVICE_PORT", "7981"))
    version = os.getenv("GEOMAG_VERSION", None)

    # configure factory
    if factory_type == "edge":
        factory = geomagio.edge.EdgeFactory(host=edge_host, port=edge_port)
    else:
        raise "Unknown factory type '%s'" % factory_type

    print("Starting webservice on %s:%d" % (webservice_host, webservice_port))
    app = geomagio.WebService(factory, version)
    httpd = make_server(webservice_host, webservice_port, app)
    httpd.serve_forever()
