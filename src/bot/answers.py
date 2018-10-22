import itertools
import os
import random

import openpyxl

from .settings import Settings


class Answers:
    def __init__(self, answer_file):
        self.location = os.path.join(Settings.assets_location, answer_file)
        self.wb = openpyxl.load_workbook(self.location)
        self.sheet = self.wb[self.wb.sheetnames[0]]

    def get(self, question, options):
        for cell in self.sheet['A']:
            if str(cell.value).replace(" ", "") == str(question).replace(" ", ""):
                row = cell.row
                number = self.sheet['B%s' % row].value
                if number == 0:
                    return list(filter(lambda a: random.choice([True, False]), options))
                else:
                    return self.get_answer(row, options, number)
        return self.new_entry(question, options)

    def save_answer(self, answer, row):
        number = self.sheet['B%s' % row].value
        wrong_answers = self.wrong_answers(row, number)
        size = len(wrong_answers)
        for i in range(number):
            offset = 3 + size * number
            self.sheet[row][offset + i].value = answer[i]
        print('saved new possible Answer: \n%s' % answer)

    def get_answer(self, row, options, number):
        answers = list(map(lambda c: c.value, self.sheet[row][2:]))
        if answers[0]:
            return answers[0:number]
        else:
            try:
                return self.new_answer(number, options, row)
            except IndexError as ie:
                print(ie)
                print("There are no new Answers for this Question: \n%s" % (row[0]))
                return options[0:number]

    def new_answer(self, number, options, row):
        possible_answers = self.possible_answers(options, row, number)
        answer = list(possible_answers[0])
        self.save_answer(answer, row)
        self.save()
        return answer

    def possible_answers(self, options, row, number):
        wrong_answers = self.wrong_answers(row, number)
        return list(map(lambda a: list(a),
                        filter(lambda a: list(a) not in wrong_answers,
                               itertools.combinations(options, number))))

    def wrong_answers(self, row, number):
        answers = list(filter(lambda a: a, map(lambda c: c.value, self.sheet[row][2:])))
        return list(filter(lambda a: a[0], self.array_split(answers, number)))

    def new_entry(self, question, options):
        number = self.extract_number(question)
        if number == 0:
            answer = options
        else:
            answer = options[:number]

        self.sheet.append([question, number, None] + answer)
        self.save()
        return answer

    def extract_number(self, question):
        if "eine" in question:
            return 1
        if "zwei" in question:
            return 2
        if "drei" in question:
            return 3
        if "vier" in question:
            return 4
        if "fünf" in question:
            return 5
        if "sechs" in question:
            return 6
        if "sieben" in question:
            return 7
        if "acht" in question:
            return 8
        if "neun" in question:
            return 9
        if "zehn" in question:
            return 10
        if "Select one answer" in question:
            return 1
        if "Select two answers" in question:
            return 2
        if "Select three answers" in question:
            return 3
        if "Select four answers" in question:
            return 4
        if "Select five answers" in question:
            return 5
        if "Select six answers" in question:
            return 6
        if "Select seven answers" in question:
            return 7
        if "Select eight answers" in question:
            return 8
        if "Select nine answers" in question:
            return 9
        if "Select ten answers" in question:
            return 10
        else:
            return 0

    def save(self):
        self.wb.save(self.location)

    def array_split(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def url(self):
        return self.sheet['A1'].value
