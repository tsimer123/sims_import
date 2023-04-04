from datetime import datetime

from handlers_files.type_data import SimFields


class SimFieldsData(SimFields):     
     state_in_lk: datetime
     last_upload: str


# создаем словарь с данными о количестве испортируемых сим карт
dict_count_import_sim = {
        'count_all': None,
        'count_new': None,
        'count_update': None,
        'count_del': None,
        'restored_del': None,
    }