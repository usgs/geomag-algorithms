## Docker

https://www.docker.com/

Docker containers bundle all dependencies needed to use geomag-algorithms.
The container includes a Jupyter Notebook server for interactive development.

### Run docker container

> This page provides one example of how to run a container. See https://docs.docker.com/engine/reference/run/ for detailed `docker run` documentation.

The following command creates and starts a container in the background.

    docker run --rm -it --name geomagio -p 8000:8000 -v $(pwd)/data:/data usgs/geomag-algorithms

- `--rm` runs a temporary container
- `-it` makes the container interactive (so you can stop it with `ctrl+c`)
- `-name geomagio` assigns the name `geomagio`
- `-p 8000:8000` forwards system port `8000` to container port `8000`
- `-v $(pwd)/data:/data` mounts a local data directory (./data) into the container so notebooks are saved
- `usgs/geomag-algorithms:latest` refers to the
  latest version of the geomag-algorithms docker image

### Use the container

- Run an interactive python prompt


      docker exec -it geomagio python

- Use the Jupyter Notebook server

  Check the output for a URL like this, that can be opened in a web browser: `http://127.0.0.1:8000/?token=...`

- Use the `geomag.py` command line interface

      docker exec -it geomagio geomag.py \
          --inchannels H E Z F \
          --input edge \
          --interval minute \
          --observatory BOU \
          --output iaga2002 \
          --output-stdout \
          --starttime 2016-07-04T00:00:00Z \
          --endtime 2016-07-04T23:59:00Z

- Stop a running container:

  Press `Ctrl+C` and follow prompts to stop the container.

### Build container

Docker images are built using the `Dockerfile` at the root of this project.

    docker build -t usgs/geomag-algorithms:TAG .
