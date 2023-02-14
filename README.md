# burn-after-reading

A service to share short term messages stored in memory. Using client side
crypto where the key is shared via the url hash.

[Demo](https://burn.blacknode.se/)

ℹ️ Consider checking out [yopass](https://github.com/jhaals/yopass) that does very much the same as this project, but is more well maintained.

## Deployment

The service is available as a docker image that you can use. Alternatively, you can also use a wsgi-server, e.g. uwsgi.
The easiest way is probably to use something like the following docker-compose file to run the service via docker.

```yml
version: "3"

services:  
  burn-after-reading:
    image: docker.pkg.github.com/tethik/burn-after-reading/burn-after-reading:latest
    environment:     
      - MAX_CONTENT_LENGTH=16777216     
      - BURN_DATA_PATH=/opt/data/     
      - BURN_MAX_STORAGE=1024   
    
    # Expose port 80
    # ports:
    #   - 80:80
    
    # Persist data
    # volumes:
    #   - /root/docker-services/burn-after-reading/data:/opt/data
```

## Configuration

The application supports configuration through the following environment variables.

```
BURN_DATA_PATH=./data/
BURN_MAX_STORAGE=1024
MAX_CONTENT_LENGTH=16777216
BURN_ALLOW_PROXY_IP=False
```

- `BURN_DATA_PATH` decides where the service should store the data. If you want to store in memory, you can use `/dev/shm`.
- `BURN_MAX_STORAGE` decides max how many documents the service will store. This is not related to the actual disk space used, only the actual count of messages currently stored.
- `MAX_CONTENT_LENGTH` is the max request size, roughly how big the document is allowed to be in bytes.
- `BURN_ALLOW_PROXY_IP` toggles whether or not to trust proxy HTTP headers rather. If the service is running behind a proxy, e.g. traefik, you may need to enable this with `BURN_ALLOW_PROXY_IP=True`.


## Tech and Credits

- [AngularJS 1](https://angularjs.org/)
- [SJCL](https://bitwiseshiftleft.github.io/sjcl/)
- [Flask](http://flask.pocoo.org/)
- [skeleton css framework](http://getskeleton.com)
- [flat circle-icons from elegantthemes.com](http://www.elegantthemes.com/blog/freebie-of-the-week/beautiful-flat-icon)
- [sqllite3](https://www.sqlite.org/)
