from bot import Answers

answers = Answers('Braindump (Windows and Devices)- Windows IoT for Device Builders_de-DE (MPN16233).xlsx')

print("FINAL Answer: %s" %
      answers.get(question='drei',
                  options=['a', 'b', 'c']))
