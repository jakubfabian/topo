#!/usr/bin/env bash
#
# Script to delete the project container and the database
docker-compose stop web
docker-compose stop db
docker-compose rm web
docker-compose rm db

docker ps -a | awk '{print $1}' | xargs --no-run-if-empty docker rm -f

if [ "$1" == "force" ]; then
   echo "== deleting also images =="
   docker rmi $(docker images -q)
fi

sudo rm -rf */migrations

