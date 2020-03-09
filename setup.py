import setuptools

setuptools.setup(
    name="geomag-algorithms",
    version="1.0.1",
    description="USGS Geomag Algorithms Library",
    url="https://github.com/usgs/geomag-algorithms",
    packages=setuptools.find_packages(exclude=["test*"]),
    python_requires=">=3.6, <4",
    install_requires=["numpy", "scipy", "obspy"],
    extras_require={
        "url": ["pycurl"],
        "webservice": [
            "authlib",
            "flask",
            "flask-login",
            "flask-migrate",
            "flask-session",
            "flask-sqlalchemy",
            "psycopg2-binary",
        ],
    },
    scripts=["bin/geomag.py", "bin/geomag_webservice.py", "bin/make_cal.py"],
    project_urls={
        "Bug Reports": "https://github.com/usgs/geomag-algorithms/issues",
        "Source": "https://github.com/usgs/geomag-algorithms",
    },
)
