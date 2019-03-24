#!/bin/sh

RUNNING="$(sudo docker ps --format 'table {{.Image}}' -f STATUS=running | grep -w instagramtools)"

while [ "$RUNNING" ]
do
    sleep 30
    RUNNING="$(sudo docker ps --format 'table {{.Image}}' -f STATUS=running | grep -w instagramtools)"
done

echo SHUTDOWN because Bot stopped
/sbin/shutdown -h now