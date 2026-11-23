from openpyxl import load_workbook
import csv
from typing import Union

from handlers_files.conf_sims import dict_fields_megafon_chenge_excel, \
    dict_fields_beeline_chenge_excel, dict_fields_mts_chenge_excel
from exceptions.exceptions import NotValidFile

class ConvertExcel:

    def __init__(self, local_route_in: str, local_route_out: str, operator_in: str) -> None:
        self.local_route_in = local_route_in
        self.local_route_out = local_route_out
        self.header_operator = operator_in
        self.sheet = None

    def excel_to_csv(self)-> None:
        self.read_excel()
        count_header = self.change_headers()
        if count_header >= 0:
            self.write_to_csv(count_header)
        else:
            raise NotValidFile('header not found in file')


    def read_excel(self)-> None:
        wb = load_workbook(self.local_route_in)
        self.sheet = wb.active


    def change_headers(self)-> int:
        count = 0        
        count_header = -1
        fields_header = self.get_fields_operator()
        if fields_header != '':
            keys_fields = list(fields_header.keys())
            for line_r in self.sheet:
                if count < 5:
                    for line_c in line_r:
                        # print(line_c.value)
                        if line_c.value in keys_fields:
                            for line_k in fields_header:
                                if line_k == line_c.value:
                                    # print(f'---origin: {line_c.value}')
                                    line_c.value = fields_header[line_k]
                                    if count_header < 0:
                                        count_header = count
                                    # print(f'---change: {line_c.value}')
                                    break                    
                count += 1
        else:
            print(f'error (ConvertExcel.change_headers): not valid in operator: {self.header_operator} for get fields header')
        return count_header    


    def write_to_csv(self, count_header: int)-> None:
        count = 0
        with open(self.local_route_out, 'w', newline="") as f:
            c = csv.writer(f)
            for line_r in self.sheet:
                if count >= count_header:
                    c.writerow([cell.value for cell in line_r]) 
                    # for line_c in line_r:
                    #     print(line_c.value)
                    #     c.writerow(line_c.value)
                count += 1


    def get_fields_operator(self)-> Union[dict, str]:
        dict_operator = ''
        if self.header_operator == 'megafon':
            dict_operator = dict_fields_megafon_chenge_excel
        if self.header_operator == 'beeline':
            dict_operator = dict_fields_beeline_chenge_excel
        if self.header_operator == 'mts':
            dict_operator = dict_fields_mts_chenge_excel        
        return dict_operator
  