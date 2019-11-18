# burn-after-reading

A service to share short term messages stored in memory. Using client side
crypto where the key is shared via the url hash.

[Demo](https://burn.blacknode.se/)

## Running locally

Python version: 3.6

```
pipenv install
```

You can either start the server locally by running

```
python run.py
```

or with gunicorn

```
gunicorn burn.wsgi
```

## Testing

```bash
py.test
```

## Configuration

The application supports configuration through environment variables and dotenv (i.e. save a `.env` file in the directory you are running the server).

Sample `.env` might look as follows.

```
BURN_DATA_PATH=./data/
BURN_MAX_STORAGE=1024
MAX_CONTENT_LENGTH=16777216
```

- `BURN_DATA_PATH` decides where the service should store the data. If you want to store in memory, you can use `/dev/shm`.
- `BURN_MAX_STORAGE` decides max how many documents the service will store. This is not related to the actual disk space used, only the actual count of messages currently stored.
- `MAX_CONTENT_LENGTH` is the max request size, roughly how big the document is allowed to be in bytes.

## Docker

There's a Dockerfile included, so the project can be run as a docker container as follows.
Still need to figure out how to set the capacity though...

```
docker build . -t burn
docker run -p 80:80 -it burn
```

## Testing

```bash
py.test
```

## Tech and Credits

- [AngularJS 1](https://angularjs.org/)
- [SJCL](https://bitwiseshiftleft.github.io/sjcl/)
- [Flask](http://flask.pocoo.org/)
- [skeleton css framework](http://getskeleton.com)
- [flat circle-icons from elegantthemes.com](http://www.elegantthemes.com/blog/freebie-of-the-week/beautiful-flat-icon)
- [sqllite3](https://www.sqlite.org/)

## Todo

See issues:
https://github.com/Tethik/burn-after-reading/issues/
