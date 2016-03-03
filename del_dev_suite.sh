#!/bin/bash
docker-compose stop web
docker-compose stop db
docker-compose rm web
docker-compose rm db

docker ps -a | awk '{print $1}' | xargs --no-run-if-empty docker rm -f
