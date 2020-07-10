"""flask app"""

import os
from datetime import datetime
import pandas as pd
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import fields, validators
from werkzeug.utils import secure_filename
from utils import init_check, is_valid_ext, insert_csv_to_db, sphere_distance, offset2datetime

app = Flask(__name__, static_folder='assets')
Bootstrap(app)
# config
app.config['host'] = '0.0.0.0'
app.config['port'] = int(os.getenv('PORT', '3463'))
app.config['SECRET_KEY'] = '1001778270'
app.config['allowed_csv_ext'] = {'csv', 'txt'}
app.config['project_dir'] = os.path.abspath(os.path.dirname(__file__))
app.config['upload_dir'] = os.path.join(app.config['project_dir'], 'assets')
app.config['db_path'] = os.path.join(app.config['upload_dir'], 'db.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + app.config['db_path']

db = SQLAlchemy(app)


# db entity
class EarthquakeInfo(db.Model):
    time = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    depth = db.Column(db.Float, nullable=False)
    mag = db.Column(db.Float, nullable=True)
    gap = db.Column(db.Float, nullable=True)
    id = db.Column(db.String(15),
                   nullable=False,
                   unique=True,
                   primary_key=True)
    place = db.Column(db.String(100), nullable=False)
    locationSource = db.Column(db.String(5), nullable=False)


# form
class FileForm(FlaskForm):
    file = fields.FileField('Earthquake CSV File')
    submit = fields.SubmitField('Submit')


class ModifyForm(FlaskForm):
    lat1 = fields.FloatField(
        'latitude 1', validators=[validators.NumberRange(min=-90, max=90)])
    long1 = fields.FloatField(
        'longitude 1', validators=[validators.NumberRange(min=-180, max=180)])
    lat2 = fields.FloatField(
        'latitude 2', validators=[validators.NumberRange(min=-90, max=90)])
    long2 = fields.FloatField(
        'longitude 2', validators=[validators.NumberRange(min=-180, max=180)])
    depth_value = fields.FloatField('Depth value')
    submit = fields.SubmitField('Submit')


class LocationForm(FlaskForm):
    location = fields.StringField('Location')
    mag = fields.FloatField('Magnitude',
                            validators=[validators.NumberRange(min=0)])
    submit = fields.SubmitField('Submit')


class DistanceForm(FlaskForm):
    location = fields.StringField('Location')
    distance = fields.FloatField('Distance',
                                 validators=[validators.NumberRange(min=0)])
    modified = fields.StringField('Modified Location')
    submit = fields.SubmitField('Submit')


# router
@app.route('/', methods=['GET', 'POST'])
def index():
    title = "Upload CSV to Database"
    form = FileForm()
    all_info = EarthquakeInfo.query.order_by(EarthquakeInfo.depth.desc()).all()
    number = len(all_info)
    result = all_info[:1]
    if form.validate_on_submit():
        upload_status = 'failed'
        filename = secure_filename(form.file.data.filename)
        if is_valid_ext(filename, app.config['allowed_csv_ext']):
            filename = os.path.join(app.config['upload_dir'], filename)
            form.file.data.save(filename)
            insert_csv_to_db(filename, EarthquakeInfo, db)
            upload_status = 'success'
            all_info = EarthquakeInfo.query.order_by(
                EarthquakeInfo.depth.desc()).all()
            number = len(all_info)
            result = all_info[:1]
        return render_template('index.html',
                               title=title,
                               form=form,
                               upload_status=upload_status,
                               number=number,
                               result=result)
    return render_template('index.html',
                           title=title,
                           form=form,
                           number=number,
                           result=result)


@app.route('/modify', methods=['GET', 'POST'])
def modify():
    title = 'Modify'
    form = ModifyForm()
    if form.validate_on_submit():
        lat1 = form.lat1.data
        lon1 = form.long1.data
        lat2 = form.lat2.data
        lon2 = form.long2.data
        depth_value = form.depth_value.data
        result = EarthquakeInfo.query
        low_lat = min(lat1, lat2)
        high_lat = max(lat1, lat2)
        low_lon = min(lon1, lon2)
        high_lon = max(lon1, lon2)
        all_info = EarthquakeInfo.query.filter(
            (EarthquakeInfo.latitude >= low_lat)
            & (EarthquakeInfo.latitude <= high_lat)
            & (EarthquakeInfo.longitude >= low_lon)
            & (EarthquakeInfo.longitude <= high_lon)).all()
        for info in all_info:
            info.depth = depth_value
        db.session.commit()
        return render_template('query.html',
                               title=title,
                               form=form,
                               result=all_info)
    return render_template('query.html', title=title, form=form)


@app.route('/location', methods=['GET', 'POST'])
def location():
    form = LocationForm()
    if form.validate_on_submit():
        location = form.location.data
        min_mag = form.mag.data
        result = EarthquakeInfo.query.filter(
            (EarthquakeInfo.mag >= min_mag)
            & (EarthquakeInfo.place == location)).order_by(
                EarthquakeInfo.time).limit(10).all()
        return render_template('query.html', form=form, result=result)
    return render_template('query.html', form=form)


@app.route('/distance', methods=['GET', 'POST'])
def distance():
    title = "The largest magnitude earthquake within {distance} from {where}"
    form = DistanceForm()
    if form.validate_on_submit():
        location = form.location.data
        distance = form.distance.data
        modified = form.modified.data
        all_info = EarthquakeInfo.query.filter(
            (EarthquakeInfo.place == location)).all()
        center_lat = 0
        center_lon = 0
        count = 0
        for info in all_info:
            center_lat += info.latitude
            center_lon += info.longitude
            count += 1
        center_lat /= count
        center_lon /= count
        all_info = EarthquakeInfo.query.order_by(
            EarthquakeInfo.mag.desc()).all()
        result = []
        for info in all_info:
            if sphere_distance([center_lat, center_lon],
                               [info.latitude, info.longitude]) <= distance:
                info.place = modified
                db.session.commit()
                result.append(info)
                break
        return render_template('query.html',
                               title=title,
                               form=form,
                               result=result)
    return render_template('query.html', title=title, form=form)


@app.errorhandler(404)
@app.route('/error_404')
def page_not_found(error):
    return render_template('404.html', title='404')


@app.errorhandler(500)
@app.route('/error_500')
def requests_error(error):
    return render_template('500.html', title='500')


if __name__ == "__main__":
    init_check(app.config['upload_dir'])
    db.create_all()
    app.run(host=app.config['host'], port=app.config['port'])