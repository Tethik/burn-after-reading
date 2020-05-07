# Development Cheatsheet

## Run tests
```
pytest
```

## Check for published security vulnerabilities
```
safety
```

## Push new docker container

```sh
VERSION=1.4.1
docker build -t docker.pkg.github.com/tethik/burn-after-reading:$VERSION .
docker push docker.pkg.github.com/tethik/burn-after-reading/burn-after-reading:$VERSION
```