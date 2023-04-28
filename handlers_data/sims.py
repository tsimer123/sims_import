import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime  

from global_var import dict_name_operators
from handlers_files.open_files import FileReaderCsv
from handlers_db.queries import get_sim_operator, write_new_sims, write_new_import_log,\
    update_change_sims, write_update_import_log
from handlers_db.sql_type_data import SimInfo, ImportSimsLogInfo, UpdateSimLogInfo
from exceptions.exceptions import NotOneOperatorInFile
from handlers_files.type_data import SimFields
from handlers_data.data_type_data import SimFieldsData


load_dotenv()

def handler_file_csv(in_dir_files: str, in_name_files: str) -> str:

    dict_count_import_sim_out = {
        'count_all': None,
        'count_new': None,
        'count_update': None,
        'count_del': None,
        'restored_del': None,
    }

    print(f'{str(datetime.now())}: start processing file: "{in_name_files}"')

    # добавление записи в ImportSimsLog о старте импорта
    import_log_info_start = ImportSimsLogInfo(
        start_import=datetime.now(),
        name_file=in_name_files
    )
    import_log_id = write_new_import_log(import_log_info_start)   

    # получение даты создания(последний модификации файла)
    date_create_file = get_create_file(in_dir_files, in_name_files)
    # получение списка из csv файла
    get_sims_csv = FileReaderCsv(in_dir_files, in_name_files)
    list_sims_csv = get_sims_csv.get_list_sims()
    # проверка файла на наличие нескольких операторов, если оператор не один упадает исключение
    # NotOneOperatorInFile('File contains more than one statement')
    check_count_operators_in_file(list_sims_csv)
    
    # получение данных из бд по оператору из csv файла
    list_sims_present_db = get_sim_operator(list_sims_csv[0]['operator'], 'present')
    list_sims_delete_db = get_sim_operator(list_sims_csv[0]['operator'], 'deleted')

    # начало обработки данных
    if len(list_sims_present_db) == 0: # если из БД ничего не вернулось, то по этому оператору нет данныз в БД, заносим все данные из csv файла
        list_sim_to_db = preparation_new_sims_for_db(list_sims_csv, date_create_file)
        write_new_sims(list_sim_to_db)
        dict_count_import_sim_out['count_new'] = len(list_sim_to_db)
    else: # в простивном случае начинамем разделять сим карты на типы (новые, обновленные, удаленные, восстановленные)   
        # создаем списки только с номерами телефонов
        list_number_tel_csv = get_number_tel_from_list_file(list_sims_csv)
        list_number_tel_present_db = get_number_tel_from_list_db(list_sims_present_db)
        list_number_tel_delete_db = get_number_tel_from_list_db(list_sims_delete_db)
        # сравниваем список номеров телефонов из csv файла со списком телефонов из БД, для посика новых сим карт 
        list_new_number_tel = diff_number_sim(list_number_tel_csv, list_number_tel_present_db)
        list_new_number_tel = diff_number_sim(list_new_number_tel, list_number_tel_delete_db)
        # создание списка с новыми симкартами и запись их в БД
        list_new_sims = new_sim_from_list(list_new_number_tel, list_sims_csv)
        if len(list_new_sims) > 0:
            list_new_sims_to_db = preparation_new_sims_for_db(list_new_sims, date_create_file)
            write_new_sims(list_new_sims_to_db)
            dict_count_import_sim_out['count_new'] = len(list_new_sims_to_db)

        
        # обработка измененных сим карт
        list_sim_change_fields = [] # список сим карт с изменеными полями
        list_updatelog_sim_change_fields = [] # список с логом изменения полей у сим карты
        # проверка сим карты на удаление из ЛК
        list_number_tel_delete_db = get_number_tel_from_list_db(list_sims_delete_db)
        list_del_number_tel = diff_number_sim(list_number_tel_present_db, list_number_tel_csv)
        # удаляем сим карты уже отмеченыее как deleted
        list_del_number_not_del_tel = diff_number_sim(list_del_number_tel, list_number_tel_delete_db)        
        if len(list_del_number_not_del_tel) > 0:
            for line_list_del_number_not_del_tel in list_del_number_not_del_tel:
                del_sim = change_sim_to_db(line_list_del_number_not_del_tel, list_sims_present_db,
                                           date_create_file, 'deleted')
                if del_sim['sims_id'] != 0:
                    list_sim_change_fields.append(del_sim)
                    list_updatelog_sim_change_fields.append(update_sim_to_db(del_sim, import_log_id))
                    if dict_count_import_sim_out['count_del'] is None:
                        dict_count_import_sim_out['count_del'] = 1
                    else:
                        dict_count_import_sim_out['count_del'] += 1

        # обрабокта сим карт появившихся в ЛК после удаления
        list_restored_number_tel = intersection_number_sim(list_number_tel_csv, list_number_tel_delete_db)
        if len(list_restored_number_tel) > 0:
            for line_list_restored_sim_tel in list_restored_number_tel:
                restored_sim = change_sim_to_db(line_list_restored_sim_tel, list_sims_delete_db,
                                                date_create_file, 'present')
                if restored_sim['sims_id'] != 0:
                    sim_in_csv_present = search_sim_in_csv(line_list_restored_sim_tel, list_sims_csv)
                    sim_in_db_present = search_sim_in_db(line_list_restored_sim_tel, list_sims_delete_db)
                    if sim_in_csv_present['hash_data'] != sim_in_db_present['hash_data']:
                        restored_sim = search_change_field(sim_in_csv_present, sim_in_db_present, restored_sim)
                    list_sim_change_fields.append(restored_sim)
                    list_updatelog_sim_change_fields.append(update_sim_to_db(restored_sim, import_log_id))
                    if dict_count_import_sim_out['restored_del'] is None:
                        dict_count_import_sim_out['restored_del'] = 1
                    else:
                        dict_count_import_sim_out['restored_del'] += 1               

        # проверка сим карты на изменение полей
        other_sim = list_number_tel_csv
        if len(list_new_sims) > 0:
            other_sim = diff_number_sim(other_sim, list_new_number_tel)
        if len(list_restored_number_tel) > 0:
            other_sim = diff_number_sim(other_sim, list_restored_number_tel) 
        if len(other_sim) > 0:
            for line_other_sim in other_sim:
                sim_in_csv = search_sim_in_csv(line_other_sim, list_sims_csv)
                sim_in_db = search_sim_in_db(line_other_sim, list_sims_present_db)
                if sim_in_csv['hash_data'] != sim_in_db['hash_data']:
                    change_fields = get_change_new_field(sim_in_csv, sim_in_db)
                    list_sim_change_fields.append(change_fields)
                    list_updatelog_sim_change_fields.append(update_sim_to_db(change_fields, import_log_id))
                    if dict_count_import_sim_out['count_update'] is None:
                        dict_count_import_sim_out['count_update'] = 1
                    else:
                        dict_count_import_sim_out['count_update'] += 1   
            # запись измененных сим карт в БД
            update_change_sims(list_sim_change_fields, list_updatelog_sim_change_fields)

    # получаем общее количество всех обработаннахы сим карт
    count_all_sims = count_all_import_sims(dict_count_import_sim_out)
    dict_count_import_sim_out['count_all'] = count_all_sims
    # подготовка сведений об обработанных сим картах и результов работы скрипта для обновления importsimslog
    import_log_info_end = ImportSimsLogInfo(
        importsimslog_id=import_log_id,
        state='successfully', 
        count_import_sim=count_all_sims,
        count_sim_file=len(list_sims_csv),
        description=count_import_sims_in_str(dict_count_import_sim_out))
    
    # обновление записи в importsimslog
    import_log_id = write_update_import_log(import_log_info_end)

    print(f'{str(datetime.now())}: end processing file: "{in_name_files}"\n--results: {import_log_info_end["description"]}')

    return list_sims_csv[0]['operator']


def check_count_operators_in_file(list_sims: list[SimFields]) -> None:
    
    tmp_list_operator = []
    for line_list_sims in list_sims:
        if line_list_sims['operator'] not in tmp_list_operator:
            tmp_list_operator.append(line_list_sims['operator'])
    if len(tmp_list_operator) > 1:
        raise NotOneOperatorInFile('File contains more than one statement')
    

def get_create_file(dir_files: str, name_files: str):
    
    dir_sims_parent = os.getenv('dir_sims_parent')
    path = Path(dir_sims_parent, dir_files, name_files)
    date_create_tstamp = os.stat(path).st_mtime
    date_create = datetime.fromtimestamp(date_create_tstamp)

    return date_create
 

def search_sim_in_csv(number_tel: str, csv: list[SimFields]) -> SimFields:    
    
    start_csv = 0
    end_csv =  len(csv) - 1

    while start_csv <= end_csv:
        mid_csv = (start_csv + end_csv) // 2
        tmp_number_tel = csv[mid_csv]['number_tel']

        if tmp_number_tel == number_tel:
            return csv[mid_csv]
        if int(tmp_number_tel) > int(number_tel):
            end_csv = mid_csv - 1
        else:
            start_csv = mid_csv + 1
        
    null_sims = SimFields(number_tel=0)
    return null_sims


def search_sim_in_db(number_tel: str, db: list[SimInfo]) -> SimInfo:    
    start_db = 0
    end_db =  len(db) - 1

    while start_db <= end_db:
        mid_db = (start_db + end_db) // 2
        tmp_number_tel = db[mid_db]['number_tel']

        if tmp_number_tel == number_tel:
            return db[mid_db]
        if int(tmp_number_tel) > int(number_tel):
            end_db = mid_db - 1
        else:
            start_db = mid_db + 1
        
    null_sims = SimInfo(sims_id=0)
    return null_sims


def preparation_new_sims_for_db(
        list_sims_in: list[SimFields],
        date_create_file: datetime) -> list[SimFieldsData]:
    
    list_sims = []

    for line_list_sims_in in list_sims_in:
        tmp_sim = SimFieldsData()
        for key, value in line_list_sims_in.items():
            tmp_sim[key] = value
        tmp_sim['state_in_lk'] = 'present'
        tmp_sim['last_upload'] = date_create_file
        list_sims.append(tmp_sim)
    
    return list_sims
        

def get_number_tel_from_list_file(list_sims: list[SimFields]) -> list:

    list_number_tel = []

    for line_list_sims in list_sims:
        list_number_tel.append(line_list_sims['number_tel'])
    
    return list_number_tel


def get_number_tel_from_list_db(list_sims: list[SimInfo]) -> list:

    list_number_tel = []

    for line_list_sims in list_sims:
        list_number_tel.append(line_list_sims['number_tel'])
    
    return list_number_tel


def diff_number_sim(list_1: list, list_2: list) -> list:

    dif_list = list(set(list_1) - set(list_2))

    return dif_list


def intersection_number_sim(list_1: list, list_2: list) -> list:

    intersection_list = list(set(list_1) & set(list_2))

    return intersection_list


def new_sim_from_list(list_new_number_tel: list, list_sims_csv: list[SimFields]) -> list[SimFields]:
    
    list_new_sims_to_db = []
    for line_list_new_number_tel in list_new_number_tel:
        tmp_sim = search_sim_in_csv(line_list_new_number_tel, list_sims_csv)
        if tmp_sim['number_tel'] != 0:
            list_new_sims_to_db.append(tmp_sim)
    return list_new_sims_to_db


def change_sim_to_db(del_number_tel: str, list_sims_present_db: list[SimInfo], last_upload, state_in_lk_in) -> SimInfo:

    del_sims_to_db = SimInfo()
    
    tmp_sim = search_sim_in_db(del_number_tel, list_sims_present_db)
    if tmp_sim['sims_id'] != 0:
        del_sims_to_db['sims_id'] = tmp_sim['sims_id']
        del_sims_to_db['state_in_lk'] = state_in_lk_in
        del_sims_to_db['last_upload'] = last_upload
    else:
        del_sims_to_db['sims_id'] = 0   
    
    return del_sims_to_db


def update_sim_to_db(sim_info: SimInfo, importsimslog_id: int) -> UpdateSimLogInfo:

    update_sim = UpdateSimLogInfo()

    for key, value in sim_info.items():
        update_sim[key] = value

    update_sim['importsimslog_id'] = importsimslog_id

    return update_sim


def get_change_new_field(csv: SimFields, db: SimInfo) -> SimInfo:
    
    change_fields = SimInfo(sims_id=db['sims_id'])

    change_fields = search_change_field(csv, db, change_fields)
    
    return change_fields


def search_change_field(csv: SimFields, db: SimInfo, change_fields: SimInfo) -> SimInfo:

    for key, value in csv.items():
        if key in db:
            if db[key] != value:
                change_fields[key] = value
    
    return change_fields


def count_all_import_sims(dict_count_import_sim_in: dict) -> int:

    count_all = 0    

    for line in dict_count_import_sim_in.values():
        if line is not None:
            count_all += line

    return count_all


def count_import_sims_in_str(dict_count_import_sim_in: dict) -> str:

    count_str = ''   

    for key, value in dict_count_import_sim_in.items():
        if value is not None:
            count_str += f'{key}: {value}, '

    count_str = count_str[:len(count_str)-2]

    return count_str