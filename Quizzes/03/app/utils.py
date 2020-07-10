"""utils funtion"""

import os
import pandas as pd
from datetime import datetime

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
    "WY": "Wyoming"
}

short_name = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI",
    "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
    "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
    "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA",
    "WV", "WI", "WY"
]

state_name = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "District of Columbia", "Florida", "Georgia",
    "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
    "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina",
    "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
    "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas",
    "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin",
    "Wyoming"
]


def init_check(*args):
    for path in args:
        if not os.path.exists(path):
            os.mkdir(path)


def is_valid_ext(filename, valid_ext=None):
    if valid_ext == None:
        return True
    _, ext = os.path.splitext(filename)
    return ext[1:] in valid_ext


def _csv2entity_list(csv_filename, Entity, flag):
    entity_list = []
    df = pd.read_csv(csv_filename)
    for _, row in df.iterrows():
        if flag == 'ti':
            entity_list.append(
                Entity(entity=row['Entity'],
                       code=row['Code'],
                       year=row['Year'],
                       num_ti=row['NumberTerroristIncidents']))
        if flag == 'sp':
            entity_list.append(
                Entity(entity=row['Entity'],
                       code=row['Code'],
                       year=row['Year'],
                       prevalence=row['Prevalence']))
    return entity_list


def _insert_entity_to_db(entity_list, Entity, db):
    for entity in entity_list:
        # result = Entity.query.filter_by(id=entity.id).first()
        # if result:
        #     result = entity
        # else:
        db.session.add(entity)
    db.session.commit()


def insert_csv_to_db(csv_filename, Entity, db, flag):
    entity_list = _csv2entity_list(csv_filename, Entity, flag)
    _insert_entity_to_db(entity_list, Entity, db)
