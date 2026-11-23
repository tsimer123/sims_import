
code_mts = '101'
code_megafon = '102'
code_beeline = '199'

dict_fields_mts = {
    'number_tel': 'msisdn',
    'iccid': 'iccid',
    'apn': 'dedicated_apn',
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

dict_fields_megafon_chenge_excel = {
    'Номер': 'MSISDN',
    'ICC': 'ICCID',
    'Название выделенной точки (APN)': 'APN',
    'Статический IP адрес': 'Статический IP',
    'Статус абонента': 'Статус',
    'Дата последней активности': 'Активность',
    'IMEI': 'IMEI'
}

dict_fields_beeline_chenge_excel = {
    'MSISDN': 'MSISDN',
    'ICCID': 'ICCID',
    'APN': 'APN',
    'IP-адрес': 'IP-адрес',
    'Фиксированный IP': 'Фиксированный IP',
    'Статус': 'Статус',
    'Передача данных (Мб)': 'Передача данных (Мб)',
    'IMEI': 'IMEI'
}

dict_fields_mts_chenge_excel = {
    'msisdn': 'msisdn',
    'iccid': 'iccid',
    'dedicated_apn': 'dedicated_apn',
    'last_ip': 'last_ip',
    'status': 'status',
    'state': 'state',
    'sum_data': 'sum_data',
    'imei': 'imei'
}