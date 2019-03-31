#!/bin/sh

docker-compose build
docker-compose push

P_USER=$1
shift


# id_rsa=$(cat ./saas-bot.pem)
# SSH_KEY=${id_rsa//
# /_}
# mkdir .env
# echo "SSH_KEY=$SSH_KEY" > .env/.manager.env
# echo ".manager.env: $(cat .env/.manager.env)"


docker-machine create --driver $@
name=${@: -1}
MANAGER_IP=$(docker-machine ip $name)
COMPOSE="docker-compose-pro.yml"

docker-machine ssh $name "sudo docker swarm init --advertise-addr $MANAGER_IP"
docker-machine scp $COMPOSE $name:
docker-machine scp -r .env/ $name:
docker-machine ssh $name "sudo docker stack deploy --compose-file $COMPOSE $name"
