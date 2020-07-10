"""utils funtion"""

import os
import math
from contextlib import contextmanager
from time import time
from datetime import datetime, timedelta
import pandas as pd
from pyecharts import charts, options

STR_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class TimeRecorder:
    def __init__(self, digits=7):
        self._digits = digits
        self._time_dict = {}
        self._is_recording = False
        self._temp_key = ''
        self._temp_tic = 0

    @property
    def is_recording(self):
        return self._is_recording

    def start_recording(self, key):
        if self.is_recording:
            raise RuntimeError(
                'The recording is already start, please run end_recording() to save this recording.'
            )
        else:
            self._is_recording = True
            self._temp_key = key
            self._temp_tic = time()

    def end_recording(self):
        if self.is_recording:
            self.add_record(self._temp_key, time() - self._temp_tic)
            self._is_recording = False
        else:
            raise RuntimeError(
                'The recording is not start, please run start_recording() first.'
            )

    @contextmanager
    def timer(self, key):
        try:
            self.start_recording(key)
            yield self
        finally:
            self.end_recording()

    def add_record(self, key, value):
        self._time_dict[key] = round(value, self._digits)

    def get_records(self, key=None):
        if key:
            return self._time_dict[key]
        else:
            return self._time_dict

    def reset_records(self):
        self._time_dict = {}


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


def get_viz(method, label, data):
    if method == 'bar':
        viz = charts.Bar()
        viz.add_xaxis(label)
        viz.add_yaxis('', data)
    elif method == 'pie':
        data = [list(d) for d in zip(label, data)]
        viz = charts.Pie()
        viz.add('', data)
        viz.set_series_opts(label_opts=options.LabelOpts(formatter="{b}: {c}"))
    return viz