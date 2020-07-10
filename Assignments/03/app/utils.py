"""utils funtion"""

import os
from time import time
from datetime import datetime
from contextlib import contextmanager
import pandas as pd

short2state = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}

lower2state = {
    "alabama": "Alabama",
    "alaska": "Alaska",
    "arizona": "Arizona",
    "arkansas": "Arkansas",
    "california": "California",
    "colorado": "Colorado",
    "connecticut": "Connecticut",
    "delaware": "Delaware",
    "district of columbia": "District of Columbia",
    "florida": "Florida",
    "georgia": "Georgia",
    "hawaii": "Hawaii",
    "idaho": "Idaho",
    "illinois": "Illinois",
    "indiana": "Indiana",
    "iowa": "Iowa",
    "kansas": "Kansas",
    "kentucky": "Kentucky",
    "louisiana": "Louisiana",
    "maine": "Maine",
    "maryland": "Maryland",
    "massachusetts": "Massachusetts",
    "michigan": "Michigan",
    "minnesota": "Minnesota",
    "mississippi": "Mississippi",
    "missouri": "Missouri",
    "montana": "Montana",
    "nebraska": "Nebraska",
    "nevada": "Nevada",
    "new hampshire": "New Hampshire",
    "new jersey": "New Jersey",
    "new mexico": "New Mexico",
    "new york": "New York",
    "north carolina": "North Carolina",
    "north dakota": "North Dakota",
    "ohio": "Ohio",
    "oklahoma": "Oklahoma",
    "oregon": "Oregon",
    "pennsylvania": "Pennsylvania",
    "rhode island": "Rhode Island",
    "south carolina": "South Carolina",
    "south dakota": "South Dakota",
    "tennessee": "Tennessee",
    "texas": "Texas",
    "utah": "Utah",
    "vermont": "Vermont",
    "virginia": "Virginia",
    "washington": "Washington",
    "west virginia": "West Virginia",
    "wisconsin": "Wisconsin",
    "wyoming": "Wyoming",
}

valid_short_name = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI",
    "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
    "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
    "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA",
    "WV", "WI", "WY"
]

valid_state_name = [
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "district of columbia", "florida", "georgia",
    "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky",
    "louisiana", "maine", "maryland", "massachusetts", "michigan", "minnesota",
    "mississippi", "missouri", "montana", "nebraska", "nevada",
    "new hampshire", "new jersey", "new mexico", "new york", "north carolina",
    "north dakota", "ohio", "oklahoma", "oregon", "pennsylvania",
    "rhode island", "south carolina", "south dakota", "tennessee", "texas",
    "utah", "vermont", "virginia", "washington", "west virginia", "wisconsin",
    "wyoming"
]


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
    """TODO: make it elegance, remove hard-code"""
    entity_list = []
    df = pd.read_csv(csv_filename, encoding='latin')
    for _, row in df.iterrows():
        entity_list.append(
            Entity(state_name=row['STNAME'],
                   county_name=row['CTYNAME'],
                   pop_est_2010=row['POPESTIMATE2010'],
                   pop_est_2011=row['POPESTIMATE2011'],
                   pop_est_2012=row['POPESTIMATE2012'],
                   pop_est_2013=row['POPESTIMATE2013'],
                   pop_est_2014=row['POPESTIMATE2014'],
                   pop_est_2015=row['POPESTIMATE2015'],
                   pop_est_2016=row['POPESTIMATE2016'],
                   pop_est_2017=row['POPESTIMATE2017'],
                   pop_est_2018=row['POPESTIMATE2018'],
                   pop_est_2019=row['POPESTIMATE2019']))
    return entity_list


def _insert_entity_to_db(entity_list, Entity, db):
    """TODO: make it elegance, remove hard-code"""
    for entity in entity_list:
        result = Entity.query.filter(
            (Entity.state_name == entity.state_name)
            & (Entity.county_name == entity.county_name)).first()
        if result:
            result = entity
        else:
            db.session.add(entity)
    db.session.commit()


def insert_csv_to_db(csv_filename, Entity, db):
    entity_list = _csv2entity_list(csv_filename, Entity)
    _insert_entity_to_db(entity_list, Entity, db)
