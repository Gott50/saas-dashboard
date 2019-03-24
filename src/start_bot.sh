#!/bin/sh
echo $SSH_KEY > ./tmp
tr '_' '\n' < ./tmp > ./id_rsa
chmod 600 ./id_rsa
rm ./tmp

IP=$1
shift

echo Dashboard Parameters: $@

scp -o StrictHostKeychecking=no -i ./id_rsa -r ./bot_scripts $P_USER@$IP:
ssh -o StrictHostKeychecking=no -tt -i ./id_rsa $P_USER@$IP "bash bot_scripts/start_bot.sh $@"