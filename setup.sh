#!/bin/sh

docker-machine create --driver $@
name=${@: -1}
MANAGER_IP=$(docker-machine ip $name)
COMPOSE="docker-compose-pro.yml"

docker-machine ssh $name "sudo docker swarm init --advertise-addr $MANAGER_IP"
docker-machine scp $COMPOSE $name:
docker-machine scp -r .env/ $name:
docker-machine ssh $name "sudo docker stack deploy --compose-file $COMPOSE $name"
