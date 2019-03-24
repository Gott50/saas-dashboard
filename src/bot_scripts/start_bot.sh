#!/bin/bash

echo "" > nohup.out

sudo service docker start
echo docker status: $(sudo service docker status)

# Delete all images
sudo docker rmi $(sudo docker images -q)

sudo docker pull gott50/saas-bot
sudo docker pull selenium/standalone-chrome:3.141.59

echo "Composition sudo docker stop /selenium"
sudo docker stop /selenium
echo "Composition sudo docker rm /selenium"
sudo docker rm /selenium
echo "Composition start /selenium"
sudo docker run -d --net=bridge --name selenium selenium/standalone-chrome:3.141.59


#USER=$USER -e PW=$PW -e SLEEP=$SLEEP -e TASKS=$TASKS
echo Composition Parameters: $@
$USER=$1
PW=$2
SLEEP=$3
shift
shift
shift
TASKS=$@


echo "Composition sudo docker stop /bot"
sudo docker stop /bot
echo "Composition sudo docker rm /bot"
sudo docker rm /bot


CMD="sudo docker run -d -v /home/ec2-user/uploads:/app/uploads --net=bridge --link selenium:selenium -e SELENIUM=selenium --name bot -e ENV=$SETTINGS -e USER=$USER -e PW=$PW -e SLEEP=$SLEEP -e TASKS=\"$TASKS\" gott50/saas-bot sh ./wait-for-selenium.sh http://selenium:4444/wd/hub -- python docker_quickstart.py"
echo Composition CMD: $CMD
$CMD

echo Start stopped_shutdown.sh
nohup sudo bash ./stopped_shutdown.sh