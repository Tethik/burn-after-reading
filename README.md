# burn-after-reading
A service to share short term messages stored in memory. Using client side
crypto where the key is shared via the url hash.

[Demo](https://burn-after-reading.herokuapp.com/)

## Running locally
Python version: 2.7

Install requirements found in requirements.txt via
```
pip install -r requirements.txt
```

You can either start the server locally by running
```
python run.py
```
or with gunicorn
```
gunicorn burn.wsgi
```

## Running on Heroku

Running on heroku should work out of the box. Just clone the repo and push it
to the heroku endpoint.


## Tech and Credits
* [AngularJS](https://angularjs.org/)
* [SJCL](https://bitwiseshiftleft.github.io/sjcl/)
* [Flask](http://flask.pocoo.org/)
* [skeleton css framework](http://getskeleton.com)
* [flat circle-icons from elegantthemes.com](http://www.elegantthemes.com/blog/freebie-of-the-week/beautiful-flat-icon)
* [sqllite3](https://www.sqlite.org/)

## Todo
* Review crypto parameters further
* Tor hidden service
* Encrypt sqlite database to prevent other processes from tampering.
* Warning when not HTTPS.
* Robots.txt, perhaps try to prevent Google from indexing further by blocking agents. More advanced: non-human behaviour?
* Proof-of-key to authorize burn operation.
