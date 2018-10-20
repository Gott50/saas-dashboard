from bot import Answers

answers = Answers('Braindump (DevOps) Azure DevOps Assessment (18473).xlsx')

print("Answer: %s" %
      answers.get(question='q', options=['a','b','c']))
