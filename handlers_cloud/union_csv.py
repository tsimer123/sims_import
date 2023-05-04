import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

from handlers_files.open_files import FileReaderCsv
from handlers_files.write_file import WriterFiles

from exceptions.exceptions import EmptyDirectory

load_dotenv()

def create_route(list_dirs: List[str]) -> str:

        route_dirs = Path()

        for line_list_dirs in list_dirs:
            route_dirs = Path(route_dirs, line_list_dirs)

        return route_dirs


def get_list_files_in_dir(str_dirs: str) -> list[str]:
      
     result = sorted(os.listdir(str_dirs))

     return result
     

def union_files(dirs_in: str, dirs_out: str) -> str:

    dir_sims_parent = os.getenv('dir_sims_parent')
    route_to_files = str(create_route([dir_sims_parent, dirs_in]))
    list_files = get_list_files_in_dir(route_to_files)    

    if len(list_files) > 0:
        reader = FileReaderCsv(dirs_in, list_files[0])
        first_files = reader.get_raw_rows()
        dialect = reader.get_dialect_csv()

        if len(list_files) >= 1:
             count_files = 1
             while len(list_files) > count_files:
                                  
                reader = FileReaderCsv(dirs_in, list_files[count_files])
                next_files = reader.get_raw_rows()

                count_str = 1
                while len(next_files) > count_str:               
                    first_files.append(next_files[count_str])
                    count_str += 1                                         

                count_files +=1
        
        writer = WriterFiles(dirs_out, first_files)
        writer.write_files(list_files[0], dialect)

        return list_files[0]
    else:
        raise EmptyDirectory('not files in dir')
