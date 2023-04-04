from handlers_files.open_files import start

from handlers_files.normal_format import NormalFormat
from handlers_data.sims import handler_file_csv
from sql.scheme import create_db

def csv():
    start()

def data():
    # file = 'simCardList_20230321_092640.csv'
    # file = 'sims_64195945940495.62936039.csv'
    # file = '20221222_Билайн_выгрузкаМ2М_MOESK_21_12.csv'

    # file = 'mts.csv'
    file = 'megafon.csv'
    # file = 'belline.csv'

    dir = 'mini_test'
    handler_file_csv(dir, file)

def create_db_start():
    create_db()


if __name__ == "__main__":
       
    data()
