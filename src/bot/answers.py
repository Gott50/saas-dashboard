import os

import openpyxl

from .settings import Settings


class Answers:
    def __init__(self, answer_file):
        self.location = os.path.join(Settings.assets_location, answer_file)
        self.wb = openpyxl.load_workbook(self.location)
        self.sheet = self.wb[self.wb.sheetnames[0]]

    def get(self, question, options):
        print(self.sheet['A'])
        for cell in self.sheet['A']:
            print(cell.value)
            if cell.value == question:
                return self.get_answer(options)
        return self.new_entry(question, options)

    def get_answer(self, options):
        return []

    def new_entry(self, question, options):
        number = self.extract_number(question)
        if number == 0:
            answer = options
            number = 1
        else:
            answer = options[:number]

        self.sheet.append([question, number] + self.create_space(number) + answer)
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
        if "one" in question:
            return 1
        if "two" in question:
            return 2
        if "three" in question:
            return 3
        if "four" in question:
            return 4
        if "five" in question:
            return 5
        if "six" in question:
            return 6
        if "seven" in question:
            return 7
        if "eight" in question:
            return 8
        if "nine" in question:
            return 9
        if "ten" in question:
            return 10
        else:
            return 0

    def create_space(self, number: int):
        out = []
        for i in range(number):
            out = out + [None]
        return out

    def save(self):
        self.wb.save(self.location)
