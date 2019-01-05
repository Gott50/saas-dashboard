import os

from bot import Bot


def create_task(username, password, answer_file, sleep=2, print=print):
    bot = init_Bot(username=username, password=password, sleep=sleep, print=print)
    try:
        print('Starting: %s' % answer_file)
        result = bot.act(answer_file=answer_file)
    except Exception as e:
        print(e)
        try:
            bot.end()
        except Exception as e2:
            print(e2)
        return e
    bot.end()

    if type(result) == str:
        return result.replace('style="display: none;"', '').replace('style="height: 460px;"', '')
    else:
        return result

def init_Bot(username, password, sleep, print=print):
    print("SELENIUM: %s" % os.environ.get('SELENIUM'))
    if os.environ.get('SELENIUM'):
        bot = Bot(username=username,
                  password=password,
                  selenium_local_session=False,
                  print=print,
                  sleep_time=sleep)
        bot.set_selenium_remote_session(
            selenium_url="http://%s:%d/wd/hub" % (os.environ.get('SELENIUM','selenium'), 4444))
    else:
        bot = Bot(username=username,
                  password=password,
                  selenium_local_session=True,
                  print=print,
                  sleep_time=sleep)
    return bot
