from webdav3.client import Client
from typing import List
from pathlib import Path

class CloudConnect:

    def __init__(self, hostname_in: str, login_in: str, password_in: str) -> Client:
        self.hostname = hostname_in
        self.login = login_in
        self.password = password_in              
    
    def create_connect(self) -> None:

        data = {
            'webdav_hostname': self.hostname,
            'webdav_login': self.login,
            'webdav_password': self.password
        }
    
        client = Client(data)

        return client

    @staticmethod
    def get_contents_in_dir(client: Client, path_in: str) -> list:

        contents_in_dir = client.list(path_in)

        return contents_in_dir
    
    @staticmethod
    def get_info_object(client, route_obj_in):

        info_object = client.list(route_obj_in)

        return info_object
    

def merging_dirs(list_dirs: List[str]) -> str:

    str_result = ''

    for line_list_dirs in list_dirs:
        str_result = str_result + line_list_dirs + '/'
    
    str_result = str_result.replace('//', '/')
    
    return str_result


def check_dir(list_dirs: List[str]) -> None:

    route_dirs = Path()

    for line_list_dirs in list_dirs:
        route_dirs = Path(route_dirs, line_list_dirs)

    if Path(route_dirs).exists() is False:
        path_dir = Path(route_dirs)
        path_dir.mkdir()
            