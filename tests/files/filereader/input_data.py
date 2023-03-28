from typing import List, TypedDict

header_megafon = ['MSISDN',
                  'Статус',
                  'ICCID',
                  'Активность',
                  'IMSI',
                  'APN',
                  'Статический IP',
                  'IMEI',
                  'Статус IMEI',
                  'Комментарий',
                  'Тарифный план',
                  'Лицевой счёт',
                  'Устройство',
                  'Инв. номер',
                  'Группы',
                  'Адрес устройства']

class SimFieldsNumber(TypedDict):     
     number_tel: List[int]
     iccid: List[int]
     apn: List[int]
     ip: List[int]
     state: List[int]
     activity: List[int]
     traffic: List[int]     
     imei: List[int]

megafon_number_fields = SimFieldsNumber(
     number_tel=[0],
     iccid=[2],
     apn=[5],
     ip=[6],
     state=[1],
     activity=[3],     
     imei=[7])

megafon_number_fields_ = SimFieldsNumber(
     number_tel=[0],
     iccid=[2],
     apn=[5],
     ip=[6],
     state=[1],
     activity=[3],     
     imei=[7, 2])