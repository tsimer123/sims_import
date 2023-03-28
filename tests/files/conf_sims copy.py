
code_mts = '101'
code_megafon = '102'
code_beeline = '199'

dict_fields_mts = {
    'number_tel': 'msisdn',
    'iccid': 'iccid',
    'apn': 'apn',
    'ip': 'last_ip',
    'state': ['status', 'state'],    
    'traffic': 'sum_data',    
    'imei': 'imei'
}

dict_fields_megafon = {
    'number_tel': 'MSISDN',
    'iccid': 'ICCID',
    'apn': 'APN',
    'ip': 'Статический IP',
    'state': 'Статус',
    'activity': 'Активность',
    'imei': 'IMEI'
}

dict_fields_beeline = {
    'number_tel': 'MSISDN',
    'iccid': 'ICCID',
    'apn': 'APN',
    'ip': ['IP-адрес', 'Фиксированный IP'],
    'state': 'Статус',    
    'traffic': 'Передача данных (Мб)',    
    'imei': 'IMEI'
}