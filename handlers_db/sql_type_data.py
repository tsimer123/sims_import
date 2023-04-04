from typing import TypedDict, Optional
from datetime import datetime

class SimInfo(TypedDict):
     sims_id: int
     number_tel: Optional[str]
     iccid: Optional[str]
     apn: Optional[str]
     ip: Optional[str]
     state: Optional[str]
     activity: Optional[str]
     traffic: Optional[str]
     operator: Optional[str]
     imei: Optional[str]
     hash_data: Optional[str]
     state_in_lk: Optional[str]
     last_upload: Optional[datetime]
     created_on: Optional[datetime]
     update_on: Optional[datetime]    


class ImportSimsLogInfo(TypedDict):
     importsimslog_id: Optional[int]
     start_import: Optional[datetime]
     name_file: Optional[str]
     state: Optional[str]
     count_import_sim: Optional[int]
     count_sim_file: Optional[int]
     description: Optional[str]
     error_import: Optional[str]
     created_on: Optional[datetime]


class UpdateSimLogInfo(TypedDict):
     updatesimlog_id: Optional[int]
     sims_id: int
     importsimslog_id: int
     number_tel: Optional[str]
     iccid: Optional[str]
     apn: Optional[str]
     ip: Optional[str]
     state: Optional[str]
     activity: Optional[str]
     traffic: Optional[str]
     operator: Optional[str]
     state_in_lk: Optional[str]
     created_on: Optional[datetime]
