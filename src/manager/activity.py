import json
import threading
from time import sleep

import subprocess
import logging
from manager.AWS import AWS


class Activity:
    def __init__(self, logger=logging):
        self.logger = logger
        self.aws = AWS(logger)

    def start_bot(self, account):
        if self.is_running(username=account['username']):
            self.logger.warning("new Thread to ReStart Bot for: %s" % account['username'])
            thread = threading.Thread(target=self.restart_account, args=(account,))
        else:
            self.logger.warning("new Thread to Start Bot for: %s" % account['username'])
            thread = threading.Thread(target=self.start_account, args=(account,))
        return thread.start()

    def is_running(self, username):
        return self.aws.get_ip(user=username)

    def start_account(self, account):
        ip = self.aws.start(user=account['username'])
        self.logger.warning("start_bot for %s at ip: %s" % (account['username'], ip))

        sleep(120)

        return self.cmd_start_bot(account, ip)

    def restart_account(self, account):
        ip = self.aws.restart(user=account['username'])
        self.logger.warning("restart for %s at ip: %s" % (account['username'], ip))

        sleep(60)

        return self.cmd_start_bot(account, ip)

    def cmd_start_bot(self, account, ip):
        self.logger.warning("run start_bot.sh on IP %s for User: %s" % (ip, account))
        json_tasks = json.dumps(account['tasks']).replace('"', '\\"').replace(" ", "")
        return subprocess.Popen(["./start_bot.sh", ip] +
                                [account['username'], account['password'], str(account['sleep']), json_tasks])
