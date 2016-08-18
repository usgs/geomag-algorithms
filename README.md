Geomag Algorithms
=================
[![Build Status](https://travis-ci.org/usgs/geomag-algorithms.svg?branch=master)](https://travis-ci.org/usgs/geomag-algorithms)


Geomag Algorithms is an open source library for processing
Geomagnetic timeseries data.  It includes algorithms and input/output factories
used by the [USGS Geomagnetism Program](http://geomag.usgs.gov) to
  translate between data formats,
  generate derived data and indices in near-realtime,
  and research and develop new algorithms.


- Accesses USGS data services.
- Built using established open source python libraries
    [NumPy](http://www.numpy.org/),
    [SciPy](http://www.scipy.org/), and
    [ObsPy](http://www.obspy.org/).
- Common geomagnetic formats including
    IAGA2002,
    IMFV122,
    IMFV283 (read only), and
    PCDCP.
- Defines command line interface, `geomag.py`.
- Embeddable Python API, `import geomagio`.


## Examples
> [More Examples in docs/example/](./docs/example/)

The following examples request data from USGS for
  `BOU` observatory,
  `H`, `E`, `Z`, and `F` component,
  `minute` interval,
  and `variation` type data
  for the day `2016-07-04`,
then write `IAGA2002` formatted output to the console.

### Command Line Interface Example
```
geomag.py \
    --input edge \
    --observatory BOU \
    --inchannels H E Z F \
    --type variation \
    --interval minute \
    --output iaga2002 \
    --output-stdout \
    --starttime 2016-07-04T00:00:00Z \
    --endtime 2016-07-04T23:59:00Z
```
[Command Line Interface documentation](./docs/cli.md)

### Python API Example
```
import sys
import geomagio
from obspy.core import UTCDateTime

input_factory = geomagio.edge.EdgeFactory()
timeseries = input_factory.get_timeseries(
    observatory = 'BOU',
    channels = ('H', 'E', 'Z', 'F'),
    type = 'variation',
    interval = 'minute',
    starttime = UTCDateTime('2016-07-04T00:00:00Z'),
    endtime = UTCDateTime('2016-07-04T23:59:00Z'))

output_factory = geomagio.iaga2002.IAGA2002Factory()
output_factory.write_file(
    channels = ('H', 'E', 'Z', 'F'),
    fh = sys.stdout,
    timeseries = timeseries)
```
[Python API documentation](./docs/api.md)


## Install
> [More Install options in docs/install.md](./docs/install.md).

### Docker
Docker is the simplest install option.

1. Create and start a new container

    named `geomagio`,
    listening on local port `8000`,
    from the image `usgs/geomag-algorithms` on docker hub

    ```
    docker run -d --name geomagio -p 8000:80 usgs/geomag-algorithms
    ```

2. Use the running container

  - Run the `geomag.py` command line interface:

    ```
    docker exec -it geomagio geomag.py
    ```

  - Run python interactively in a web browser:

    ```
    open http://localhost:8000
    ```

    > In the top right corner, choose "New" then "Python 2"


## Algorithms
[Algorithms described in docs/algorithms/](./docs/algorithms)


## Developing
[Developing described in docs/develop.md](./docs/develop.md).


## License
[License described in LICENSE.md](./LICENSE.md)


## Problems or Questions?

- [Report an issue using the GitHub issue tracker](http://github.com/usgs/geomag-algorithms/issues)
- [Join the USGS geomag-data mailing list](https://geohazards.usgs.gov/mailman/listinfo/geomag-data)
- [Email jmfee at usgs.gov](mailto:jmfee@usgs.gov)


## Additional Links

- [USGS Geomagnetism Program Home Page](http://geomag.usgs.gov/)
- [Waffle Project Board](https://waffle.io/usgs/geomag-algorithms)
