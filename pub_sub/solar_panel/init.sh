#/bin/bash

docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker rmi solar_gen
docker build -t solar_gen:latest .
