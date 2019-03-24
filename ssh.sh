#!/bin/bash

ssh -o StrictHostKeychecking=no -tt -i saas-bot.pem ec2-user@$1
