import threading
from time import sleep

import subprocess

from manager.AWS import AWS


class Activity:
    def __init__(self, logger):
        self.logger = logger
        self.aws = AWS(logger)

    def start_bot(self, account):
        if not self.is_running(username=account.username):
            print("Start new Thread for Bot: %s" % account.username)
            thread = threading.Thread(target=self.start_account, args=(account,))
            return thread.start()

    def is_running(self, username):
        return self.aws.get_ip(user=username)

    def start_account(self, account):
        ip = self.aws.start(user=account.username)
        self.logger.warning("start_bot for %s at ip: %s" % (account.username, ip))

        sleep(120)

        return subprocess.Popen(["./start_bot.sh"] +
                                [ip, account.username, account.password])
