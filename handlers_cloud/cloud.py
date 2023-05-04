from webdav3.client import Client
from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import datetime
import shutil

from handlers_db.queries import get_root_dir_cloud
from handlers_cloud.logics import get_list_start_dirs, walker_dirs_cloud
from handlers_cloud.cloudconnect import CloudConnect

load_dotenv()


def nahdler_connect_cloud(start_date_cloud_in: str) -> None:
    
    print(f'{str(datetime.now())}: start import sim')

    start_date_cloud = start_date_cloud_in    
    cloud_hostname = os.getenv('cloud_hostname')
    cloud_login = os.getenv('cloud_login')
    cloud_password = os.getenv('cloud_password')
    dir_root = os.getenv('dir_root')

    cloud = CloudConnect(
        cloud_hostname,
        cloud_login,
        cloud_password        
    )

    client = cloud.create_connect()
    path_root = dir_root
    # получение из облака всех директорий в корневой директории
    root_dirs_cloud = cloud.get_contents_in_dir(client, path_root)
    # подготовка списка директорий из облака - исключение / и файлов
    prcsd_root_dirs_cloud = get_list_start_dirs(root_dirs_cloud, start_date_cloud)
    # получение директорий из БД
    root_dirs_db = get_root_dir_cloud()
    # запуск обработки новых директорий из облака
    result = walker_dirs_cloud(prcsd_root_dirs_cloud, client, cloud,
                      path_root, root_dirs_db)
    print(f'{str(datetime.now())}: sim import result')
    for line_result in result:
        print(f"--{line_result['name']} {str(line_result['state'])}")

    root_dir = os.getenv('dir_sims_parent')
    del_dir = os.listdir(root_dir)
    for line_del_dir in del_dir:
        shutil.rmtree(Path(root_dir, line_del_dir))

    print(f'{str(datetime.now())}: end import sim')
