from typing import List, TypedDict
from datetime import datetime


class SimFieldsNumber(TypedDict):     
     number_tel: List[int]
     iccid: List[int]
     apn: List[int]
     ip: List[int]
     state: List[int]
     activity: List[int]
     traffic: List[int]     
     imei: List[int]


class SimFields(TypedDict):     
     number_tel: str
     iccid: str
     apn: str
     ip: str
     state: str
     activity: datetime
     traffic: str    
     imei: str 
     hash_tuple: int