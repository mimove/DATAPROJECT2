#/bin/bash

docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker rmi test
docker build -t test:latest .
