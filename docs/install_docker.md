## Docker
https://www.docker.com/

Docker containers bundle all dependencies needed to use geomag-algorithms.
The container includes a Jupyter Notebook server for interactive development.

> Docker images are built using the `Dockerfile` at the root of this project.


### Create a new docker container

The following command creates and starts a container.
```
docker run -d --name geomagio -p 8000:80 usgs/geomag-algorithms
```

- `-d` runs container in the background
- `-name geomagio` assigns the name `geomagio`
- `-p 8000:80` forwards system port `8000` to container port `80`
- `usgs/geomag-algorithms:latest` refers to the
  latest version of the geomag-algorithms docker image

  > Notebooks are stored in the container in the directory `/notebooks`


### Use the container

- Start a stopped container:
```
docker start geomagio
```

- Run an interactive python prompt
```
docker exec -it geomagio python
```

- Use the Jupyter Notebook server
```
open http://localhost:8000/
```

- Use the `geomag.py` command line interface
```
docker exec -it geomagio geomag.py \
    --inchannels H E Z F \
    --input edge \
    --interval minute \
    --observatory BOU \
    --output iaga2002 \
    --output-stdout \
    --starttime 2016-07-04T00:00:00Z \
    --endtime 2016-07-04T23:59:00Z
```

- Stop a running container:
```
docker stop geomagio
```
