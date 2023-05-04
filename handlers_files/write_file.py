import csv
from pathlib import Path
from typing import List


class WriterFiles:

    def __init__(self, list_dirs_in: str, list_rows_in: List[List[str]]) -> None:
        self.list_dirs = list_dirs_in
        self.list_rows = list_rows_in

    
    @staticmethod
    def create_route(list_dirs: List[str]) -> str:

        route_dirs = Path()

        for line_list_dirs in list_dirs:
            route_dirs = Path(route_dirs, line_list_dirs)

        return route_dirs

    
    def write_files(self, name_file: str, dialect) -> None:

        route_files = self.create_route([self.list_dirs, name_file])

        with open(str(route_files), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, dialect, doublequote=True)
            writer.writerows(self.list_rows)
