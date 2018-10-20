from bot import Bot

bot = Bot(username='timo.morawitz@outlook.com',
          password="Di1.WeDiLeSe")

bot.act(
    url='https://partneruniversity.microsoft.com/?whr=uri:MicrosoftAccount&courseId=18473&scoId=5IpOumJVF_2313787008',
    answer_file='Braindump (DevOps) Azure DevOps Assessment (18473).xlsx')

bot.end()
