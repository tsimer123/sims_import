import locale
import re
from datetime import datetime

from handlers_files.type_data import SimFields

class NormalFormat:

    # переписать под список

    def _init_(self) -> None:
        pass

    @staticmethod
    def normal_number_tel(sim_info: SimFields) -> SimFields:

        if len(sim_info['number_tel']) < 11:
            if sim_info['number_tel'][0] != 7:
                sim_info['number_tel'] = '7' + sim_info['number_tel']
                       
        return sim_info
    
    
    @staticmethod
    def normal_ip(sim_info: SimFields) -> SimFields:

        tamplate_ip = r'^([1-2])?([1-9])?([0-9]{1})\.(([1-2])?([1-9])?([0-9]{1}))\.(([1-2])?([1-9])?([0-9]{1}))\.(([1-2])?([1-9])?([0-9]{1}))$'

        if sim_info['ip'] != '':
            if re.fullmatch(tamplate_ip, sim_info['ip']):
                return sim_info
            else:
                tmp_ip = sim_info['ip'].split('.')
                count = 0
                while count < len(tmp_ip):
                    tmp_ip[count] = int(tmp_ip[count])
                    count += 1

                if len(tmp_ip) == 4:
                    normal_ip = str(tmp_ip[0]) + '.' + str(tmp_ip[1]) + '.' + str(tmp_ip[2]) + '.' + str(tmp_ip[3])
                    sim_info['ip'] = normal_ip
                    return sim_info
                else:
                    print('bad format ip to sim: ' + sim_info['number_tel'] + ' - ' + sim_info['ip'])
                    return sim_info
        else:
             return sim_info     

     
    def normal_activity(self, sim_info: SimFields) -> SimFields:

        if 'activity' in sim_info and sim_info['activity'] != '':
            try:
                tmp_date = sim_info['activity']
                tmp_date = self.replace_month_str_to_int(tmp_date)
                datetime_object = datetime.strptime(tmp_date, "%d %m %Y %H:%M")
                sim_info['activity'] = datetime_object
            except Exception as ex:
                print(str(ex.args))
                print('bad format activity to sim: ' + sim_info['number_tel'] + ' - ' + sim_info['activity'])  
        return sim_info
        
    
    @staticmethod
    def replace_month_str_to_int(str_date: str) -> str:

        RU_MONTH_VALUES = {
            'января': '01',
            'февраля': '02',
            'марта': '03',
            'апреля': '04',
            'мая': '05',
            'июня': '06',
            'июля': '07',
            'августа': '08',
            'сентября': '09',
            'октября': '10',
            'ноября': '11',
            'декабря': '12',
            }
        
        tmp_date = str_date.replace('г., ', '')

        for key, value in RU_MONTH_VALUES.items():
            tmp_date = tmp_date.replace(key, value)

        return tmp_date




            