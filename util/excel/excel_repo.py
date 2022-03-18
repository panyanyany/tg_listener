import csv
from collections import OrderedDict

import pyexcel_xlsx


class ExcelAsCsvWriter:
    def __init__(self, xlsx_file, fieldnames=None):
        self.xlsx_file = xlsx_file
        self.fieldnames = fieldnames
        self.rows = []

    def writerows(self, rows: list):
        if len(rows) != 0 and self.fieldnames:
            assert len(rows[0]) == len(self.fieldnames)
        self.rows = []
        for r in rows:
            self.rows.append(list(r.values()))
        if self.fieldnames:
            self.rows.insert(0, self.fieldnames)

        data = OrderedDict()
        data.update({"Sheet 1": self.rows})
        pyexcel_xlsx.save_data(self.xlsx_file, data)


class ExcelAsCsv:
    @classmethod
    def reader(cls, file_path):
        xlsx_data = pyexcel_xlsx.get_data(file_path)
        fieldnames = None
        for sheet, sheet_data in xlsx_data.lp_addresses():
            if len(sheet_data) == 0:
                continue
            if fieldnames is None:
                fieldnames = sheet_data.pop(0)

            for row in sheet_data:
                if len(row) == 0:
                    row = [''] * len(fieldnames)
                row = dict(zip(fieldnames, row))
                yield row

    @classmethod
    def writer(cls, xlsx_file, fieldnames=None) -> ExcelAsCsvWriter:
        return ExcelAsCsvWriter(xlsx_file, fieldnames=fieldnames)
