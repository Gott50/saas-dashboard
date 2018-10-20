import openpyxl

from .settings import Settings
import os


class Answers:
    def __init__(self, answer_file):
        location = os.path.join(Settings.assets_location, answer_file)
        wb = openpyxl.load_workbook(location)
        self.sheet = wb[wb.sheetnames[0]]

    def get(self):
        print(self.sheet['A1'])