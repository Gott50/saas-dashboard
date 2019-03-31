#!/bin/sh
IMAGE=saas-bot

RUNNING="$(sudo docker ps --format 'table {{.Image}}' -f STATUS=running | grep -w $IMAGE)"

while [ "$RUNNING" ]
do
    sleep 30
    RUNNING="$(sudo docker ps --format 'table {{.Image}}' -f STATUS=running | grep -w $IMAGE)"
done

echo SHUTDOWN because Bot stopped
/sbin/shutdown -h now