import os
import setuptools
import setuptools.ssl_support

# configure ssl certifiate bundle from environment, if set
ssl_cert_file = os.environ.get("SSL_CERT_FILE") or os.environ.get("PIP_CERT")
if ssl_cert_file:
    setuptools.ssl_support.cert_paths = [ssl_cert_file]

setuptools.setup(
    name="geomag-algorithms",
    version="1.0.0",
    description="USGS Geomag Algorithms Library",
    url="https://github.com/usgs/geomag-algorithms",
    packages=setuptools.find_packages(exclude=["test*"]),
    project_urls={
        "Bug Reports": "https://github.com/usgs/geomag-algorithms/issues",
        "Source": "https://github.com/usgs/geomag-algorithms",
    },
    python_requires=">=3.6, <4",
    scripts=["bin/geomag.py", "bin/geomag_webservice.py", "bin/make_cal.py"],
    setup_requires=["setuptools-pipfile",],
    use_pipfile=True,
    entry_points={
        "console_scripts": ["magproc-prepfiles=geomagio.processing.magproc:main"],
    },
)
