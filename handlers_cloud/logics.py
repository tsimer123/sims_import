from typing import List
from webdav3.client import Client
from pathlib import Path
import re
import zipfile
from datetime import datetime

from handlers_cloud.cloudconnect import CloudConnect, merging_dirs, check_dir
from handlers_cloud.union_csv import union_files
from handlers_data.sims import handler_file_csv
from handlers_db.sql_type_data import DirsInfo, ContentsDirsInfo
from handlers_db.queries import write_new_dirs, get_objs_cloud, write_new_contentsdirs,\
    write_update_dirs

from exceptions.exceptions import EmptyDirectory


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
    local_rout_to_file = str(Path('sims_files', line_list_cloud, line_contents))
    check_dir(['sims_files', line_list_cloud])
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
    local_rout_to_file = str(Path('sims_files', line_list_cloud, line_contents))
    check_dir(['sims_files', line_list_cloud])
    client.download_sync(remote_path=remote_rout_to_file,
                            local_path=local_rout_to_file)
    
    archive = local_rout_to_file
    route_to_extract = Path('sims_files', line_list_cloud)
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
    local_rout_to_file = str(Path('sims_files', line_list_cloud, line_contents))
    check_dir(['sims_files', line_list_cloud])
    client.download_sync(remote_path=remote_rout_to_file,
                            local_path=local_rout_to_file)                    
    
    route_in_files = str(Path(line_list_cloud, line_contents))
    route_out_file = str(Path('sims_files', line_list_cloud))
    
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
            if dirs_new_info['state'] is not None:                
                write_update_dirs(dirs_new_info)
                dict_dir_cloud["state"] = dirs_new_info['state']          
        
        result.append(dict_dir_cloud)
        print(f'{str(datetime.now())}: stop dir {line_list_cloud}')
    
    return result
  