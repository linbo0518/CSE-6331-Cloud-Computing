"""utils funtion"""

import os
import math
from contextlib import contextmanager
from time import time
from datetime import datetime, timedelta
import pandas as pd
from pyecharts import charts, options


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
        entity_list.append(
            Entity(entity=row['Entity'],
                   code=row['Code'],
                   year=row['Year'],
                   smokers=row['Smokers']))
    return entity_list


def _insert_entity_to_db(entity_list, Entity, db):
    for entity in entity_list:
        result = Entity.query.filter_by(id=entity.id).first()  # TODO: check
        if result:
            result = entity
        else:
            db.session.add(entity)
    db.session.commit()


def insert_csv_to_db(csv_filename, Entity, db):
    entity_list = _csv2entity_list(csv_filename, Entity)
    _insert_entity_to_db(entity_list, Entity, db)


def get_viz(method, label, data):
    if method == 'bar':
        viz = charts.Bar()
        viz.add_xaxis(label)
        viz.add_yaxis('', data)
        viz.reversal_axis()
        viz.set_series_opts(label_opts=options.LabelOpts(position="right"))
    elif method == 'pie':
        data = [list(d) for d in zip(label, data)]
        viz = charts.Pie()
        viz.add('', data)
        viz.set_series_opts(label_opts=options.LabelOpts(formatter="{b}: {c}"))
    elif method == 'scatter':

        min_val = min(data)
        max_val = max(data)
        viz = charts.Scatter()
        viz.add_xaxis(label)
        viz.add_yaxis('', data)
        viz.set_global_opts(
            xaxis_opts=options.AxisOpts(
                type_="value",
                min_=label[0],
                max_=label[-1],
                splitline_opts=options.SplitLineOpts(is_show=True)),
            yaxis_opts=options.AxisOpts(
                type_="value",
                splitline_opts=options.SplitLineOpts(is_show=True)),
        )
    return viz