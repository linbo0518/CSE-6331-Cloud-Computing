"""utils funtion"""

import os
import math
from datetime import datetime, timedelta, date
import pandas as pd

STR_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def init_check(*args):
    for path in args:
        if not os.path.exists(path):
            os.mkdir(path)


def is_valid_ext(filename, valid_ext=None):
    if valid_ext == None:
        return True
    _, ext = os.path.splitext(filename)
    return ext[1:] in valid_ext


def _csv2entity_list(csv_filename, Entity):
    entity_list = []
    df = pd.read_csv(csv_filename, skipinitialspace=True)
    for _, row in df.iterrows():
        time = datetime.strptime(row['time'], STR_DATETIME_FORMAT)
        updated = datetime.strptime(row['updated'], STR_DATETIME_FORMAT)
        entity_list.append(
            Entity(time=time,
                   latitude=row['latitude'],
                   longitude=row['longitude'],
                   depth=row['depth'],
                   mag=row['mag'],
                   magType=row['magType'],
                   nst=row['nst'],
                   gap=row['gap'],
                   dmin=row['dmin'],
                   rms=row['rms'],
                   net=row['net'],
                   id=row['id'],
                   updated=updated,
                   place=row['place'],
                   type=row['type'],
                   horizontalError=row['horizontalError'],
                   depthError=row['depthError'],
                   magError=row['magError'],
                   magNst=row['magNst'],
                   status=row['status'],
                   locationSource=row['locationSource'],
                   magSource=row['magSource']))
    return entity_list


def _insert_entity_to_db(entity_list, Entity, db):
    for entity in entity_list:
        result = Entity.query.filter_by(id=entity.id).first()
        if result:
            result = entity
        else:
            db.session.add(entity)
    db.session.commit()


def insert_csv_to_db(csv_filename, Entity, db):
    entity_list = _csv2entity_list(csv_filename, Entity)
    _insert_entity_to_db(entity_list, Entity, db)


def sphere_distance(x, y, r=6371.0):

    lat1 = math.radians(x[0])
    lon1 = math.radians(x[1])
    lat2 = math.radians(y[0])
    lon2 = math.radians(y[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(
        dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return c * r


def offset2datetime(base_datetime, days):
    return base_datetime - timedelta(days)
