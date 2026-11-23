from typing import List
from webdav3.client import Client
from pathlib import Path
import re
import zipfile
from datetime import datetime
import os
from dotenv import load_dotenv


from handlers_cloud.cloudconnect import CloudConnect, merging_dirs, check_dir
from handlers_cloud.union_csv import union_files
from handlers_data.sims import handler_file_csv
from handlers_db.sql_type_data import DirsInfo, ContentsDirsInfo
from handlers_db.queries import write_new_dirs, get_objs_cloud, write_new_contentsdirs,\
    write_update_dirs
from handlers_files.excel_converter import ConvertExcel

from exceptions.exceptions import EmptyDirectory

load_dotenv()

def replace_name_dirs_cloud(list_dirs: List[str]) -> List[str]:

    replace_list = []

    tampalate_dir = r'^(202)([0-9]{5})/$'

    for line_list_dirs in list_dirs:
        if re.fullmatch(tampalate_dir, str(line_list_dirs)):        
            replace_list.append(line_list_dirs.replace('/', ''))

    return replace_list


def get_list_start_dirs(list_dirs: List[str], start_date_cloud: str) -> List[str]:

    start_list_dir = []

    repl_list_dirs = replace_name_dirs_cloud(list_dirs)

    for line_repl_dirs in repl_list_dirs:
        if int(line_repl_dirs) >= int(start_date_cloud):
            start_list_dir.append(line_repl_dirs)

    start_list_dir.sort()
    
    return start_list_dir


def get_list_dir_to_list(list_db_in: List[DirsInfo]) -> List[str]:

    list_db = []
    
    for line_list_db in list_db_in:
        list_db.append(line_list_db['name_dir'])
    
    return list_db


def find_new_dirs_cloud(list_cloud: List[str], list_db: List[str]) -> List[str]:
    
    list_new_dirs = []

    for line_list_cloud in list_cloud:        
        if line_list_cloud not in list_db:
            list_new_dirs.append(line_list_cloud)

    return list_new_dirs


def get_list_objs_to_list(list_objs_in: List[ContentsDirsInfo]) -> List[str]:

    list_objs = []

    for line_list_objs_in in list_objs_in:
        list_objs.append(line_list_objs_in['name_obj'])
    
    return list_objs


def write_dir_in_db(name_dir: str) -> DirsInfo:

    dirs_info = DirsInfo(
        name_dir=name_dir
    )

    dirs_info_out = write_new_dirs(dirs_info)

    result = DirsInfo(
        dirs_id=dirs_info_out.dirs_id,
        name_dir=dirs_info_out.name_dir,
        state=dirs_info_out.state
    )

    return result


def handler_csv(path_route: str, line_contents: str, client: Client,
                     line_list_cloud: str, dirs_id_in: int) -> str:    

    remote_rout_to_file = merging_dirs([path_route, line_contents])    
    local_rout_to_file = str(Path(os.getenv('dir_sims_parent'), line_list_cloud, line_contents))
    check_dir([os.getenv('dir_sims_parent'), line_list_cloud])
    client.download_sync(remote_path=remote_rout_to_file,
                            local_path=local_rout_to_file)                    
    operator = handler_file_csv(line_list_cloud, line_contents)

    obj_info = ContentsDirsInfo(
        dirs_id=dirs_id_in,
        name_obj=line_contents,
        state='completed'
    )

    write_new_contentsdirs(obj_info)

    return operator


def handler_zip(path_route: str, line_contents: str, client: Client,
                     line_list_cloud: str, dirs_id_in: int) -> str:
    
    remote_rout_to_file = merging_dirs([path_route, line_contents])    
    local_rout_to_file = str(Path(os.getenv('dir_sims_parent'), line_list_cloud, line_contents))
    check_dir([os.getenv('dir_sims_parent'), line_list_cloud])
    client.download_sync(remote_path=remote_rout_to_file,
                            local_path=local_rout_to_file)
    
    archive = local_rout_to_file
    route_to_extract = Path(os.getenv('dir_sims_parent'), line_list_cloud)
    with zipfile.ZipFile(archive, 'r') as zip_file:
        zip_file.extractall(route_to_extract)

    content = line_contents.replace('.zip', '')
    operator = handler_file_csv(line_list_cloud, content)

    obj_info = ContentsDirsInfo(
        dirs_id=dirs_id_in,
        name_obj=line_contents,
        state='completed'
    )

    write_new_contentsdirs(obj_info)

    return operator


def handler_mgf(path_route: str, line_contents: str, client: Client,
                     line_list_cloud: str, dirs_id_in: int) -> str:    

    remote_rout_to_file = merging_dirs([path_route, line_contents])    
    local_rout_to_file = str(Path(os.getenv('dir_sims_parent'), line_list_cloud, line_contents))
    check_dir([os.getenv('dir_sims_parent'), line_list_cloud])
    client.download_sync(remote_path=remote_rout_to_file,
                            local_path=local_rout_to_file)                    
    
    route_in_files = str(Path(line_list_cloud, line_contents))
    route_out_file = str(Path(os.getenv('dir_sims_parent'), line_list_cloud))
    
    try:
        name_out_files = union_files(route_in_files, route_out_file)    
        operator = handler_file_csv(line_list_cloud, name_out_files)
    except EmptyDirectory as ex:
        name_out_files = str(ex.args[0])
        operator = ''


    obj_info = ContentsDirsInfo(
        dirs_id=dirs_id_in,
        name_obj=line_contents,
        additions=name_out_files,
        state='completed'
    )

    write_new_contentsdirs(obj_info)

    return operator


# def handler_ex_(path_route: str, line_contents: str, client: Client,
#                      line_list_cloud: str, dirs_id_in: int) -> str:
    
#     print(f'{str(datetime.now())}: start handler_ex')

#     remote_rout_to_file = merging_dirs([path_route, line_contents])    
#     local_rout_to_file = str(Path(os.getenv('dir_sims_parent'), line_list_cloud, line_contents))
#     check_dir([os.getenv('dir_sims_parent'), line_list_cloud])
#     client.download_sync(remote_path=remote_rout_to_file,
#                             local_path=local_rout_to_file)
#     list_files_excel = sorted(os.listdir(local_rout_to_file))
#     try:
#         name_file_csv = None
#         operator = ''
#         print(f'{str(datetime.now())}: start processing excel dir')
#         for line in list_files_excel:
#             if 'megafon' in str(line).lower() or 'мегафон' in str(line).lower():
#                 print(f'{str(datetime.now())}: start processing handler_ex megafon')
#                 local_rout_to_file_ex_in = str(Path(local_rout_to_file, line))
#                 name_file_csv = line.replace('.xlsx', '.csv')
#                 local_rout_to_file_ex_out = str(Path(os.getenv('dir_sims_parent'), line_list_cloud, name_file_csv))
#                 excel_c = ConvertExcel(local_rout_to_file_ex_in, local_rout_to_file_ex_out)
#                 excel_c.excel_to_csv()
#                 print(f'{str(datetime.now())}: csv file from excel ready')
#                 if Path(local_rout_to_file_ex_out).exists():
#                     print(f'{str(datetime.now())}: push csv file megafon in handler csv')
#                     operator = handler_file_csv(line_list_cloud, name_file_csv)
#                     print(f'{str(datetime.now())}: good result csv file megafon in handler csv')
#                 else:
#                    print(f'{str(datetime.now())}: bad result csv file megafon in handler csv')
#                    raise EmptyDirectory(f'Not file {name_file_csv}')
#                 print(f'{str(datetime.now())}: end processing handler_ex megafon')
#     except EmptyDirectory as ex:
#         name_file_csv = str(ex.args)
#         operator = ''

#     print(f'{str(datetime.now())}: end processing excel dir')
#     if name_file_csv is not None:
#         obj_info = ContentsDirsInfo(
#             dirs_id=dirs_id_in,
#             name_obj=name_file_csv,
#             state='completed'
#         )

#         write_new_contentsdirs(obj_info)
#     print(f'{str(datetime.now())}: end processing handler_ex megafon')

#     return operator


def handler_ex(path_route: str, line_contents: str, client: Client,
                     line_list_cloud: str, dirs_id_in: int) -> str:
    
    print(f'{str(datetime.now())}: start handler_ex')

    remote_rout_to_file = merging_dirs([path_route, line_contents])    
    local_rout_to_file = str(Path(os.getenv('dir_sims_parent'), line_list_cloud, line_contents))
    check_dir([os.getenv('dir_sims_parent'), line_list_cloud])
    client.download_sync(remote_path=remote_rout_to_file,
                            local_path=local_rout_to_file)
    list_files_excel = sorted(os.listdir(local_rout_to_file))
    
    print(f'{str(datetime.now())}: start processing excel dir')
    operator_out = ''
    for line in list_files_excel:
        if 'megafon' in str(line).lower() or 'мегафон' in str(line).lower():
            operator = iter_excel_dir('megafon', local_rout_to_file, line,
                                      line_list_cloud, dirs_id_in)
            operator_out = operator_out + ' ' + operator
        if 'beeline' in str(line).lower() or 'билайн' in str(line).lower():
            operator = iter_excel_dir('beeline', local_rout_to_file, line,
                                      line_list_cloud, dirs_id_in)
            operator_out = operator_out + ' ' + operator
        if 'mts' in str(line).lower() or 'мтс' in str(line).lower():
            operator = iter_excel_dir('mts', local_rout_to_file, line,
                                      line_list_cloud, dirs_id_in)
            operator_out = operator_out + ' ' + operator

    print(f'{str(datetime.now())}: end processing excel dir')

    print(f'return operator_out: {operator_out}')

    operator_out = operator_out.strip()
    return operator_out


def iter_excel_dir(name_operator: str, local_rout_to_file: Path, line: str,
                   line_list_cloud: str, dirs_id_in: int)-> str:
    
    operator = ''
    name_file_csv = None
    try:        
        print(f'{str(datetime.now())}: start processing handler_ex {name_operator}')
        local_rout_to_file_ex_in = str(Path(local_rout_to_file, line))
        name_file_csv = line.replace('.xlsx', '.csv')
        local_rout_to_file_ex_out = str(Path(os.getenv('dir_sims_parent'), line_list_cloud, name_file_csv))
        excel_c = ConvertExcel(local_rout_to_file_ex_in, local_rout_to_file_ex_out, name_operator)
        excel_c.excel_to_csv()
        print(f'{str(datetime.now())}: csv file from excel ready')
        if Path(local_rout_to_file_ex_out).exists():
            print(f'{str(datetime.now())}: push csv file {name_operator} in handler csv')
            operator = handler_file_csv(line_list_cloud, name_file_csv)
            print(f'{str(datetime.now())}: good result csv file {name_operator} in handler csv')
        else:
            print(f'{str(datetime.now())}: bad result csv file {name_operator} in handler csv')
            raise EmptyDirectory(f'Not file {name_file_csv}')
        print(f'{str(datetime.now())}: end processing handler_ex {name_operator}')
    except EmptyDirectory as ex:
        # name_file_csv = str(ex.args)
        print(f'{str(datetime.now())}: error (iter_excel_dir): name line - {line}, ex.args={str(ex.args)}')
    
    if name_file_csv is not None:
        obj_info = ContentsDirsInfo(
            dirs_id=dirs_id_in,
            name_obj=name_file_csv,
            state='completed'
        )
        write_new_contentsdirs(obj_info)

    print(f'return operator: {operator}')
    return operator

    
def walker_dirs_cloud(list_cloud: List[str], client: Client, cloud: CloudConnect,
                      dir_root: str, list_db: List[DirsInfo]) -> List[dict]:

    result = []
    # перебор всех директорий в корне
    for line_list_cloud in list_cloud:
        print(f'--------------\n{str(datetime.now())}: start dir {line_list_cloud}')
        dict_dir_cloud = {
            "name": line_list_cloud,
            "state": 'Not data'
            }
        # перебор директорий из БД
        trigger_dirs_in_db = 0
        for line_list_db in list_db:            
            dirs_info = line_list_db
            # проверка директории на наличие в БД            
            if line_list_cloud == line_list_db['name_dir']:
                dict_dir_cloud["state"] = line_list_db['state']
                trigger_dirs_in_db = 1
                # если в БД уже есть директория
                # запрашиваем в БД списоок объектов содержащиеся в данной директории
                objs_line_list_db = get_objs_cloud(line_list_db['dirs_id']) 
                # запрашиваем в облаке списоок объектов содержащиеся в данной директории
                path_route = merging_dirs([dir_root, line_list_cloud])                 
                contents = cloud.get_contents_in_dir(client, path_route)
                if len(contents) > 0:
                    # получаем список с названиями объектов из БД
                    line_list_objs_name_db = get_list_objs_to_list(objs_line_list_db)
                    for line_contents in contents:
                        if line_contents not in line_list_objs_name_db:
                            # если такого файла нет в БД то подбираем метод его парсинга если требуется
                            if line_contents[-4:] == '.csv':
                                operator = handler_csv(
                                    path_route, line_contents, client, line_list_cloud, line_list_db['dirs_id']
                                )
                                if dirs_info['state'] is not None:
                                    dirs_info['state'] = dirs_info['state'] + ' ' + operator
                                else:
                                    dirs_info['state'] = operator
                            if line_contents[-4:] == '.zip':
                                operator = handler_zip(
                                    path_route, line_contents, client, line_list_cloud, line_list_db['dirs_id']
                                )
                                if dirs_info['state'] is not None:
                                    dirs_info['state'] = dirs_info['state'] + ' ' + operator
                                else:
                                    dirs_info['state'] = operator
                            if line_contents == 'Мегафон/':
                                operator = handler_mgf(
                                    path_route, line_contents, client, line_list_cloud, line_list_db['dirs_id']
                                )
                                if dirs_info['state'] is not None:
                                    dirs_info['state'] = dirs_info['state'] + ' ' + operator
                                else:
                                    dirs_info['state'] = operator
                            if line_contents == 'Excel/':
                                operator = handler_ex(
                                    path_route, line_contents, client, line_list_cloud, line_list_db['dirs_id']
                                )
                                if dirs_info['state'] is not None:
                                    dirs_info['state'] = dirs_info['state'] + ' ' + operator
                                else:
                                    dirs_info['state'] = operator
                if dirs_info['state'] == dict_dir_cloud["state"]:
                    dict_dir_cloud["state"] = 'Not data in dir'
                else:
                    write_update_dirs(dirs_info)
                    if dirs_info['state'] is not None:
                        if dict_dir_cloud['state'] is not None:
                            dict_dir_cloud["state"] = dirs_info["state"].replace(dict_dir_cloud['state'], '').replace(' ', '')
                        else:
                            dict_dir_cloud["state"] = dirs_info["state"]
                break
        if trigger_dirs_in_db == 0:            
            # записываем папку в БД
            dirs_new_info = write_dir_in_db(line_list_cloud)
            # запрашиваем в облаке списоок объектов содержащиеся в данной директории
            path_route = merging_dirs([dir_root, line_list_cloud])               
            contents = cloud.get_contents_in_dir(client, path_route)
            if len(contents) > 0:
                for line_contents in contents:                        
                    # подбираем метод его парсинга
                    if line_contents[-4:] == '.csv':
                        operator = handler_csv(
                            path_route, line_contents, client, line_list_cloud, dirs_new_info['dirs_id']
                        )
                        if dirs_new_info['state'] is not None:
                            dirs_new_info['state'] = dirs_new_info['state'] + ' ' + operator
                        else:
                            dirs_new_info['state'] = operator
                    if line_contents[-4:] == '.zip':
                        operator = handler_zip(
                            path_route, line_contents, client, line_list_cloud, dirs_new_info['dirs_id']
                        )
                        if dirs_new_info['state'] is not None:
                            dirs_new_info['state'] = dirs_new_info['state'] + ' ' + operator
                        else:
                            dirs_new_info['state'] = operator
                    if line_contents == 'Мегафон/':
                        operator = handler_mgf(
                            path_route, line_contents, client, line_list_cloud, dirs_new_info['dirs_id']
                        )
                        if dirs_new_info['state'] is not None:
                            dirs_new_info['state'] = dirs_new_info['state'] + ' ' + operator
                        else:
                            dirs_new_info['state'] = operator
                    if line_contents == 'Excel/':
                        operator = handler_ex(
                            path_route, line_contents, client, line_list_cloud, line_list_db['dirs_id']
                                )
                        if dirs_new_info['state'] is not None:
                            dirs_new_info['state'] = dirs_new_info['state'] + ' ' + operator
                        else:
                            dirs_new_info['state'] = operator
            if dirs_new_info['state'] is not None:                
                write_update_dirs(dirs_new_info)
                dict_dir_cloud["state"] = dirs_new_info['state']          
        
        result.append(dict_dir_cloud)
        print(f'{str(datetime.now())}: stop dir {line_list_cloud}')
    
    return result
  