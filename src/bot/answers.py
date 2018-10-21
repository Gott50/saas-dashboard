import openpyxl

from .settings import Settings
import os


class Answers:
    def __init__(self, answer_file):
        self.location = os.path.join(Settings.assets_location, answer_file)
        self.wb = openpyxl.load_workbook(self.location)
        self.sheet = self.wb[self.wb.sheetnames[0]]

    def get(self, question, options=[]):
        print(self.sheet['A'])
        for cell in self.sheet['A']:
            print(cell.value)
            if(cell.value == question):
                return self.get_answer(options)
        return self.new_entry(question, options)

    def get_answer(self, options):
        return []

    def new_entry(self, quesiton, options):
        number = self.extract_number(quesiton)
        answer = options[:number]
        self.sheet.append([quesiton, number] + self.create_space(number) + options[:number])
        self.save()
        return answer

    def extract_number(self, quesiton):
        if "zwei" in quesiton:
            return 2
        if "drei" in quesiton:
            return 3
        if "vier" in quesiton:
            return 4
        if "fünf" in quesiton:
            return 5
        if "sechs" in quesiton:
            return 6
        if "sieben" in quesiton:
            return 7
        if "acht" in quesiton:
            return 8
        if "neun" in quesiton:
            return 9
        if "zehn" in quesiton:
            return 10
        else:
            return 1

    def create_space(self, number: int):
        out = []
        for i in range(number):
            out = out + [None]
        return out

    def save(self):
        self.wb.save(self.location)
