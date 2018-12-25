import os
from bot import Bot


def create_task(username, password, answer_file):
    bot = init_Bot(username=username, password=password)
    try:
        print('Starting: %s' % answer_file)
        bot.act(answer_file=answer_file)
    except Exception as e:
        print(e)
        try:
            bot.end()
        except Exception as e2:
            print(e2)
        return e
    bot.end()
    return True


def init_Bot(username, password, print=print):
    bot = Bot(username=username,
              password=password,
              selenium_local_session=False,
              print=print)
    bot.set_selenium_remote_session(
        selenium_url="http://%s:%d/wd/hub" % (os.environ.get('SELENIUM', 'selenium'), 4444))
    return bot
