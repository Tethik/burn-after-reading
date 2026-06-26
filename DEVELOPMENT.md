# Development Cheatsheet

### Running locally

Set up the python virtual environment via uv.

```sh
uv sync
```

From the virtual environment, you can start the server in a debug mode by running:

```sh
uv run debug.py
```

## Run tests

```sh
uv run pytest
```

## Test docker

```sh
docker build -t .
docker run -p 5000:80 --rm -it burn
```

## Push new docker container

Should be handled by the github workflow. Just push a new tag.
