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

## Docker

There's a Dockerfile included, so the project can be run as a docker container as follows.
Still need to figure out how to set the capacity though...

```
docker build . -t burn
docker -p 80:80 run -t burn
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
