from bot import Bot

bot = Bot(username='timo.morawitz@outlook.com',
          password="Di1.WeDiLeSe")

bot.act(
    answer_file='Braindump (Windows and Devices)- Windows IoT for Device Builders_de-DE (MPN16233).xlsx')

bot.end()
