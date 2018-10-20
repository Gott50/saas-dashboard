import openpyxl

from .settings import Settings
import os


class Answers:
    def __init__(self, answer_file):
        location = os.path.join(Settings.assets_location, answer_file)
        wb = openpyxl.load_workbook(location)
        self.sheet = wb[wb.sheetnames[0]]

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
        return options