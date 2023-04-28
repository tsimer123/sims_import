from sqlalchemy.orm import sessionmaker
from typing import List
from sqlalchemy import update
from datetime import datetime

from global_var import dict_name_operators

from sql.engine import engine
from sql.scheme import Sims, ImportSimsLog, UpdateSimLog, Dirs, ContentsDirs

from handlers_db.sql_type_data import SimInfo, ImportSimsLogInfo, UpdateSimLogInfo,\
    DirsInfo, ContentsDirsInfo
from handlers_data.data_type_data import SimFieldsData

Session = sessionmaker(engine)
session = Session()


def get_sim_operator(operator_in: str, state_in_lk: str) -> list[SimInfo]:

    list_sim = []

    try:
        sim_info = session.query(Sims).filter(
            Sims.operator == operator_in,
            Sims.state_in_lk == state_in_lk).order_by(Sims.number_tel).all()
        for line_sim_info in sim_info:
            list_sim.append(format_one_sim_info(line_sim_info))        
    except Exception as ex:
        raise ex
    finally:
        session.close()

    return list_sim


def format_one_sim_info(sim_info) -> SimInfo:    

    if sim_info is not None:
        dict_sim_info = SimInfo(
            sims_id = sim_info.sims_id,
            number_tel = sim_info.number_tel,
            iccid = sim_info.iccid,
            apn = sim_info.apn,
            ip = sim_info.ip,
            state = sim_info.state,
            activity = sim_info.activity,
            traffic = sim_info.traffic,
            operator = sim_info.operator,
            imei = sim_info.imei,
            hash_data = sim_info.hash_data,
            state_in_lk = sim_info.state_in_lk,
            last_upload = sim_info.last_upload,
            created_on = sim_info.created_on,
            update_on = sim_info.update_on

        )
    else:
        dict_sim_info = SimInfo(sims_id = 0)       

    return dict_sim_info


def write_new_sims(list_sims_in: list[SimFieldsData]) -> None:

    list_sims = []

    for line_list_sims_in in list_sims_in:
        list_sims.append(format_in_sims_db(line_list_sims_in))
    
    session.add_all(list_sims)

    session.commit()
        

def format_in_sims_db(sim_info_in: SimFieldsData) -> Sims: 
    
    sim_info = Sims(
        number_tel = sim_info_in['number_tel'],
        iccid = sim_info_in['iccid'],
        apn = sim_info_in['apn'],
        ip = sim_info_in['ip'],
        state  = sim_info_in['state'],
        imei = sim_info_in['imei'],
        hash_data = sim_info_in['hash_data'],
        state_in_lk = sim_info_in['state_in_lk'],
        last_upload = sim_info_in['last_upload']       
    )

    if sim_info_in['operator'] == 'Мегафон':
        sim_info.operator = sim_info_in['operator']
        if 'activity' in sim_info_in:
            sim_info.activity = sim_info_in['activity']

    if sim_info_in['operator'] == 'МТС':
        sim_info.operator = sim_info_in['operator']
        sim_info.traffic = sim_info_in['traffic']

    if sim_info_in['operator'] == 'Билайн':
        sim_info.operator = sim_info_in['operator']
        sim_info.traffic = sim_info_in['traffic']

    return sim_info


def write_new_import_log(info_import: ImportSimsLogInfo) -> ImportSimsLogInfo:
    
    import_log = format_in_import_log(info_import)

    session.add(import_log)

    session.commit()

    import_log_id = import_log.importsimslog_id

    return import_log_id


def write_update_import_log(info_import: ImportSimsLogInfo):   
    
    session.execute(update(ImportSimsLog),[info_import],)    

    session.commit() 


def format_in_import_log(import_log_in: ImportSimsLogInfo) -> ImportSimsLog:

    import_log = ImportSimsLog()

    if 'start_import' in import_log_in:
        import_log.start_import = import_log_in['start_import']

    if 'name_file' in import_log_in:
        import_log.name_file = import_log_in['name_file']
    
    if 'state' in import_log_in:
        import_log.state = import_log_in['state']

    if 'count_import_sim' in import_log_in:
        import_log.count_import_sim = import_log_in['count_import_sim']
    
    if 'description' in import_log_in:
        import_log.description = import_log_in['description']

    if 'error_import' in import_log_in:
        import_log.error_import = import_log_in['error_import']

    return import_log


def update_change_sims(change_sims: list[SimInfo], change_log: list[UpdateSimLogInfo]) -> None:
    
    # update_sim = format_change_sim(change_sims)
    update_log = format_update_log(change_log)

    try:
        session.execute(update(Sims),change_sims,)
        # session.add_all(update_sim)
        session.add_all(update_log)
        session.commit()
    except Exception as ex:
        print(ex.args)
        print("Возврат назад...")
        session.rollback()


def format_change_sim(change_sims: list[SimInfo]) -> List[Sims]:

    list_sims = []

    for line_change_sims in change_sims:
        tmp_sim = Sims()
        tmp_sim.sims_id = line_change_sims['sims_id']
        if 'number_tel' in line_change_sims:
            tmp_sim.number_tel = line_change_sims['number_tel']

        if 'iccid' in line_change_sims:
            tmp_sim.iccid = line_change_sims['iccid']

        if 'apn' in line_change_sims:
            tmp_sim.apn = line_change_sims['apn']

        if 'ip' in line_change_sims:
            tmp_sim.ip = line_change_sims['ip']

        if 'state' in line_change_sims:
            tmp_sim.state = line_change_sims['state']

        if 'activity' in line_change_sims:
            tmp_sim.activity = line_change_sims['activity']

        if 'traffic' in line_change_sims:
            tmp_sim.traffic = line_change_sims['traffic']

        if 'operator' in line_change_sims:
            tmp_sim.operator = line_change_sims['operator']

        if 'imei' in line_change_sims:
            tmp_sim.imei = line_change_sims['imei']

        if 'hash_data' in line_change_sims:
            tmp_sim.hash_data = line_change_sims['hash_data']

        if 'state_in_lk' in line_change_sims:
            tmp_sim.state_in_lk = line_change_sims['state_in_lk']

        if 'last_upload' in line_change_sims:
            tmp_sim.last_upload = line_change_sims['last_upload']
        
        list_sims.append(tmp_sim)
            
    return list_sims


def format_update_log(change_log: list[UpdateSimLogInfo]) -> List[UpdateSimLogInfo]:
    
    list_update = []

    for line_change_log in change_log:
        tmp_update = UpdateSimLog()
        tmp_update.sims_id = line_change_log['sims_id']
        tmp_update.importsimslog_id = line_change_log['importsimslog_id']

        if 'number_tel' in line_change_log:
            tmp_update.number_tel = line_change_log['number_tel']
        
        if 'iccid' in line_change_log:
            tmp_update.iccid = line_change_log['iccid']

        if 'apn' in line_change_log:
            tmp_update.apn = line_change_log['apn']

        if 'ip' in line_change_log:
            tmp_update.ip = line_change_log['ip']

        if 'state' in line_change_log:
            tmp_update.state = line_change_log['state']

        if 'activity' in line_change_log:
            tmp_update.activity = line_change_log['activity']

        if 'traffic' in line_change_log:
            tmp_update.traffic = line_change_log['traffic']

        if 'operator' in line_change_log:
            tmp_update.operator = line_change_log['operator']

        if 'state_in_lk' in line_change_log:
            tmp_update.state_in_lk = line_change_log['state_in_lk']

        list_update.append(tmp_update)
            
    return list_update


def get_root_dir_cloud() -> List[DirsInfo]:

    list_dir = []

    try:
        dir_info = session.query(Dirs).order_by(Dirs.name_dir).all()
        for line_dir_info in dir_info:
            list_dir.append(format_one_dir_info_cloud(line_dir_info))        
    except Exception as ex:
        raise ex
    finally:
        session.close()

    return list_dir


def format_one_dir_info_cloud(dir_info: Dirs) -> DirsInfo:    

    if dir_info is not None:
        dict_dir_info = DirsInfo(
            dirs_id = dir_info.dirs_id,
            name_dir = dir_info.name_dir,
            state = dir_info.state,
            created_on = dir_info.created_on,
            update_on = dir_info.update_on            
        )
    else:
        dict_dir_info = DirsInfo(dirs_id = 0)       

    return dict_dir_info


def get_objs_cloud(dirs_id: int) -> List[ContentsDirsInfo]:
    
    list_objs = []

    try:
        objs_info = session.query(ContentsDirs).filter(
            ContentsDirs.dirs_id == dirs_id
            ).order_by(ContentsDirs.contentsdirs_id).all()
        for line_objs_info in objs_info:
            list_objs.append(format_one_objs_cloud(line_objs_info))        
    except Exception as ex:
        raise ex
    finally:
        session.close()

    return list_objs


def format_one_objs_cloud(objs_info: ContentsDirs) -> ContentsDirsInfo:    

    if objs_info is not None:
        dict_objs_info = ContentsDirsInfo(
            contentsdirs_id = objs_info.contentsdirs_id,
            dirs_id = objs_info.dirs_id,
            name_obj = objs_info.name_obj,
            state = objs_info.state,
            created_on = objs_info.created_on,
            update_on = objs_info.update_on            
        )
    else:
        dict_objs_info = ContentsDirsInfo(dirs_id = 0)       

    return dict_objs_info


def write_new_dirs(info_dir: DirsInfo) -> Dirs:
    
    dir = format_in_dirs(info_dir)

    session.add(dir)

    session.commit()

    return dir


def write_update_dirs(dirs_import: Dirs):   

    session.execute(update(Dirs),[dirs_import],)    

    session.commit() 


def format_in_dirs(info_dir_in: DirsInfo) -> Dirs:

    dir = Dirs()

    if 'dirs_id' in info_dir_in:
        dir.dirs_id = info_dir_in['dirs_id']
    if 'name_dir' in info_dir_in:
        dir.name_dir = info_dir_in['name_dir']
    if 'state' in info_dir_in:
        dir.state = info_dir_in['state'] 

    return dir


def write_new_contentsdirs(info_contents: ContentsDirsInfo) -> None:
    
    contents = format_in_contentsdirs(info_contents)

    session.add(contents)

    session.commit()


def format_in_contentsdirs(info_contents_in: ContentsDirsInfo) -> ContentsDirs:

    info_contents = ContentsDirs()

    if 'dirs_id' in info_contents_in:
        info_contents.dirs_id = info_contents_in['dirs_id']
    if 'name_obj' in info_contents_in:
        info_contents.name_obj = info_contents_in['name_obj']
    if 'additions' in info_contents_in:
        info_contents.additions = info_contents_in['additions']
    if 'state' in info_contents_in:
        info_contents.state = info_contents_in['state']
    
    return info_contents
