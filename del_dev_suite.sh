#!/usr/bin/env bash
#
# Script to delete the project container and the database
docker-compose stop web
docker-compose stop db
docker-compose rm web
docker-compose rm db

docker ps -a | awk '{print $1}' | xargs --no-run-if-empty docker rm -f
docker rmi $(docker images -q)

sudo rm -rf */migrations

