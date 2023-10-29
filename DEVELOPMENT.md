# Development Cheatsheet

### Running locally

Set up the python virtual environment via pipenv.

```
pipenv install
```

From the virtual environment, you can start the server in a debug mode by running:

```
python debug.py
```

## Run tests

```
pytest
```

## Check for published security vulnerabilities

```
safety check
```

## Test docker

```sh
docker build -t .
docker run -p 5000:80 --rm -it burn
```

## Push new docker container

Should be handled by the github workflow. Just push a new tag.
