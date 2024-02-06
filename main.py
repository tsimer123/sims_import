from datetime import datetime

from handlers_files.open_files import start

from handlers_files.normal_format import NormalFormat
from handlers_data.sims import handler_file_csv
from sql.scheme import create_db
from handlers_cloud.cloud import nahdler_connect_cloud

def csv():
    start()

def data():   
    
    file = 'belline.csv'
    dir = 'mini_test'

    handler_file_csv(dir, file)

def create_db_start():
    create_db()

def cloud():
    date_now = str(datetime.now().date()).replace('-', '')
    # date_now = "20231123"
    try:    
        nahdler_connect_cloud(date_now)
    except Exception as ex:
        print(f'{str(datetime.now())}: error: {str(ex.args)}')


if __name__ == "__main__":
    cloud()
