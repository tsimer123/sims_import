import csv
import os
from chardet import detect
import time
from datetime import datetime
import hashlib

from dotenv import load_dotenv
from pathlib import Path
from typing import List, TypedDict

from handlers_files.conf_sims import code_mts, code_megafon, code_beeline,\
dict_fields_mts, dict_fields_megafon, dict_fields_beeline
from exceptions.exceptions import NotValidOperator, NotValidFile
from handlers_files.normal_format import NormalFormat
from handlers_files.type_data import SimFields, SimFieldsNumber

load_dotenv()

class FileReader():

    def __init__(self, in_dir_files: str, in_name_files: str) -> None:
        self.name_files = in_name_files
        self.dir_files = in_dir_files


    def _get_path_files(self) -> Path:
    
        dir_sims_parent = os.getenv('dir_sims_parent')
        path = Path(dir_sims_parent, self.dir_files, self.name_files)

        return path


    def _set_field_size_limit(self) -> None:

        name_files = self._get_path_files()

        # получаем размер файла в МБ
        size = os.path.getsize(name_files) / (1024 * 1024)        

        # получаем количество строк в файле в пропорции 1 Мб на 10к строк
        count_str = size * 10000
        count_str_int = int(round(count_str, 0))       
        # устанавливаем размер field_size_limit равный count_str_int
        csv.field_size_limit(count_str_int)


    def _get_encoding(self) -> str:

        try:            
            path_files = self._get_path_files()

            with open(path_files,'rb') as f:
                tmp = detect(f.read())               
            encoding_file = tmp['encoding']

            return encoding_file

        except Exception as ex:
            print(ex.args)
            raise ex


    @staticmethod
    def get_operator(list_row: list) -> str:

        count = 0
        number_iccid = None
        
        for line in list_row:
            if count < 1:          
                try:
                    number_iccid = line.index('iccid')
                except:
                    try:
                        number_iccid = line.index('ICCID')
                    except:
                        raise NotValidFile('Not valid header')
            elif count == 1:
                if number_iccid is None:
                    raise NotValidFile('Not valid files')                    
                else:
                    iccid = line[number_iccid]
                    if iccid[4:7] == code_mts:
                        return 'МТС'
                    if iccid[4:7] == code_megafon:
                        return 'Мегафон'
                    if iccid[4:7] == code_beeline:
                        return 'Билайн'
                    raise NotValidFile('Not valid operator')
            else:                
                raise NotValidFile('Not valid files')
            
            count += 1

   
    def get_numbers_fields(self, headers: list) -> SimFieldsNumber:
        
        if self.operator == 'МТС':
            dict_fields = dict_fields_mts
        if self.operator == 'Мегафон':
            dict_fields = dict_fields_megafon
        if self.operator == 'Билайн':
            dict_fields = dict_fields_beeline
        if self.operator == 'Not valid operator':
            raise NotValidOperator('Not valid operator')
        
        numbers_field = SimFieldsNumber()
        
        for line_key, line_value in dict_fields.items():
            try:
                if isinstance(line_value, list):
                    tmp_list = []
                    for line in line_value:
                        tmp_list.append(headers.index(line))
                    numbers_field[line_key] = tmp_list
                else:
                    numbers_field[line_key] = [headers.index(line_value)]     

            except Exception as ex:                
                raise ex

        return numbers_field 
    

    def get_sims_info(self, row: list) -> SimFields:

        sim_info = SimFields()    
        
        for key, value in self.numbers_fields.items():
            if len(value) > 1:
                tmp_list_value = []
                for line_value in value:
                    tmp_list_value.append(row[line_value])
                if tmp_list_value.count(tmp_list_value[0]) == len(tmp_list_value):
                    sim_info[key] = tmp_list_value[0]

                else:
                    tmp_str = '_'.join(tmp_list_value)                    
                    while len(tmp_str) > 0:
                        if tmp_str[0] == '_':                    
                            if len(tmp_str) > 1:
                                tmp_str = tmp_str[1:]
                            else:
                                tmp_str = ''                        
                        else:
                            break
                    while len(tmp_str) > 0:
                        if tmp_str[len(tmp_str)-1] == '_':
                            if len(tmp_str) > 1:                        
                                tmp_str = tmp_str[:len(tmp_str)-1]
                            else:
                                tmp_str = ''
                        else:
                            break

                    sim_info[key] = tmp_str                    
            else:
                try:
                    a = key
                    b = row[value[0]]
                    sim_info[a] = b
                except:
                    a = key
                    sim_info[a] = 'empty'
                    print("not valid row " + sim_info['number_tel'])
            
        sim_info['operator'] = self.operator
        
        return sim_info 
    
    
    @staticmethod
    def normal_format_sim(sim_info: SimFields) -> SimFields:

        normal_format = NormalFormat()

        sim_info = normal_format.normal_number_tel(sim_info)
        if sim_info['number_tel'] != 0:
            sim_info = normal_format.normal_ip(sim_info)
            sim_info = normal_format.normal_activity(sim_info)
            sim_info = normal_format.normal_traffic(sim_info)            

        return sim_info
    

    @staticmethod
    def calc_hash_for_data(sim_info: SimFields) -> SimFields:
        
        str_temp = ''

        for line_value in sim_info.values():
            str_temp = str_temp + str(line_value)            

        b_str_temp = bytes(str_temp, 'utf-8')           
        str_sim_hashlib = hashlib.sha3_256(b_str_temp).hexdigest()
        sim_info['hash_data'] = str_sim_hashlib

        return sim_info


class FileReaderCsv(FileReader):
    
    def get_operator_csv(self, csvfile, dialect) -> str:

        count = 0
        list_row = []

        csvfile.seek(0)
        reader = csv.reader(csvfile, dialect)

        for row in reader:
            if count < 3:
                list_row.append(row)
            else: break
            count += 1
        
        operator = self.get_operator(list_row)

        return operator

        
    def get_list_sims(self) -> list[SimFields]:

        path_files = self._get_path_files()
        encoding_file = self._get_encoding()

        list_sims = []
        
        with open(path_files, newline='', encoding=encoding_file) as csvfile:
            
            # operator = self.get_operator(csvfile)

            csvfile.seek(0)
            dialect = csv.Sniffer().sniff(csvfile.readline())
            # dialect =dialect.doublequote = True
            
            self.operator = self.get_operator_csv(csvfile, dialect)

            csvfile.seek(0)
            # reader = csv.reader(csvfile, dialect='excel')
            reader = csv.reader(csvfile, dialect, doublequote=True)

            count = 0
            for row in reader:                          
                if count < 1:                              
                    self.numbers_fields = self.get_numbers_fields(row)
                else:
                    sim_info = self.get_sims_info(row)
                    normal_sim_info = self.normal_format_sim(sim_info)
                    if normal_sim_info['number_tel'] != 0:
                        hash_sim_info = self.calc_hash_for_data(normal_sim_info)
                        list_sims.append(hash_sim_info)
                count += 1
        list_sims.sort(key=lambda x: x['number_tel'])
        print(f'Total lines in file: {count-1}')
        return list_sims


def start():

    file = 'simCardList_20230321_092640.csv'
    # file = 'sims_64195945940495.62936039.csv'
    # file = '20221222_Билайн_выгрузкаМ2М_MOESK_21_12.csv'
    dir = 'test'

    get_sims = FileReaderCsv(dir, file)

    a = get_sims.get_list_sims()

    print(1)