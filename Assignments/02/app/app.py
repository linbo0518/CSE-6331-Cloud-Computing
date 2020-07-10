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
    magType = db.Column(db.String(10), nullable=True)
    nst = db.Column(db.Integer, nullable=True)
    gap = db.Column(db.Float, nullable=True)
    dmin = db.Column(db.Float, nullable=True)
    rms = db.Column(db.Float, nullable=False)
    net = db.Column(db.String(5), nullable=False)
    id = db.Column(db.String(15),
                   nullable=False,
                   unique=True,
                   primary_key=True)
    updated = db.Column(db.DateTime, nullable=False)
    place = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(15), nullable=False)
    horizontalError = db.Column(db.Float, nullable=True)
    depthError = db.Column(db.Float, nullable=True)
    magError = db.Column(db.Float, nullable=True)
    magNst = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(10), nullable=False)
    locationSource = db.Column(db.String(5), nullable=False)
    magSource = db.Column(db.String(5), nullable=False)


# form
class FileForm(FlaskForm):
    file = fields.FileField('Earthquake CSV File')
    submit = fields.SubmitField('Submit')


class TopNForm(FlaskForm):
    top_n = fields.IntegerField(
        "Top N Largest",
        validators=[validators.NumberRange(min=1, max=10)],
    )
    submit = fields.SubmitField('Submit')


class DistanceForm(FlaskForm):
    latitude = fields.FloatField(
        'Latitude (Arlington is 32.729641)',
        validators=[validators.NumberRange(min=-90, max=90)])
    longitude = fields.FloatField(
        'Longitude (Arlington is -97.110566)',
        validators=[validators.NumberRange(min=-180, max=180)])
    distance = fields.FloatField(
        'Distance within (KM)',
        validators=[validators.NumberRange(min=0)],
    )
    submit = fields.SubmitField('Submit')


class DateForm(FlaskForm):
    start_date = fields.DateField('Start date (yyyy-mm-dd)')
    end_date = fields.DateField('End date (yyyy-mm-dd)')
    magnitude = fields.FloatField(
        'Richter Magnitude Scale (greater than)',
        validators=[validators.NumberRange(min=0, max=10)])
    submit = fields.SubmitField('Submit')


class MagScaleForm(FlaskForm):
    recent_days = fields.IntegerField(
        'Recent days', validators=[validators.NumberRange(min=0)])
    low_mag = fields.IntegerField(
        'Low Richter magnitude scale',
        validators=[validators.NumberRange(min=1, max=10)])
    high_mag = fields.IntegerField(
        'High Richter magnitude scale',
        validators=[validators.NumberRange(min=1, max=10)])
    submit = fields.SubmitField('Submit')


class CompareForm(FlaskForm):
    loc1_latitude = fields.FloatField(
        'Latitude of Location 1 (Anchorage is 61)',
        validators=[validators.NumberRange(min=-90, max=90)])
    loc1_longitude = fields.FloatField(
        'Longitude of Location 1 (Anchorage is -150)',
        validators=[validators.NumberRange(min=-180, max=180)])
    loc2_latitude = fields.FloatField(
        'Latitude of Location 2 (Dallas is 32.8)',
        validators=[validators.NumberRange(min=-90, max=90)])
    loc2_longitude = fields.FloatField(
        'Longitude of Location 2 (Dallas is -96.8)',
        validators=[validators.NumberRange(min=-180, max=180)])
    distance = fields.FloatField(
        'Distance within (KM)',
        validators=[validators.NumberRange(min=0)],
    )
    submit = fields.SubmitField('Submit')


class LargestForm(FlaskForm):
    latitude = fields.FloatField(
        'Latitude (Dallas is 32.8)',
        validators=[validators.NumberRange(min=-90, max=90)])
    longitude = fields.FloatField(
        'Longitude (Dallas is -96.8)',
        validators=[validators.NumberRange(min=-180, max=180)])
    distance = fields.FloatField(
        'Distance within (KM)',
        validators=[validators.NumberRange(min=0)],
    )
    submit = fields.SubmitField('Submit')


# router
@app.route('/', methods=['GET', 'POST'])
def index():
    title = "Upload CSV to Database"
    form = FileForm()
    if form.validate_on_submit():
        upload_status = 'failed'
        filename = secure_filename(form.file.data.filename)
        if is_valid_ext(filename, app.config['allowed_csv_ext']):
            filename = os.path.join(app.config['upload_dir'], filename)
            form.file.data.save(filename)
            insert_csv_to_db(filename, EarthquakeInfo, db)
            upload_status = 'success'
        return render_template('index.html',
                               title=title,
                               form=form,
                               upload_status=upload_status)
    return render_template('index.html', title=title, form=form)


@app.route('/top_n', methods=['GET', 'POST'])
def top_n():
    title = "Top {N} Largest Earthquakes"
    form = TopNForm()
    if form.validate_on_submit():
        top_n = form.top_n.data
        result = EarthquakeInfo.query.order_by(
            EarthquakeInfo.mag.desc()).limit(top_n).all()
        return render_template('query.html',
                               title=title,
                               form=form,
                               result=result)
    return render_template('query.html', title=title, form=form)


@app.route('/distance', methods=['GET', 'POST'])
def distance():
    title = "Earthquakes within {distance} of {where}"
    form = DistanceForm()
    if form.validate_on_submit():
        distance = form.distance.data
        latitude = form.latitude.data
        longitude = form.longitude.data
        all_info = EarthquakeInfo.query.all()
        result = []
        for info in all_info:
            if sphere_distance([latitude, longitude],
                               [info.latitude, info.longitude]) <= distance:
                result.append(info)
        return render_template('query.html',
                               title=title,
                               form=form,
                               result=result)
    return render_template('query.html', title=title, form=form)


@app.route('/date', methods=['GET', 'POST'])
def date():
    title = "How many earthquakes between {date1} and {date2} greater than {magnitude}"
    form = DateForm()
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        magnitude = form.magnitude.data
        print(type(start_date))
        result = EarthquakeInfo.query.filter(
            (EarthquakeInfo.time >= start_date)
            & (EarthquakeInfo.time <= end_date)
            & (EarthquakeInfo.mag > magnitude)).all()
        return render_template('query.html',
                               title=title,
                               form=form,
                               result=result)
    return render_template('query.html', title=title, form=form)


@app.route('/scale', methods=['GET', 'POST'])
def scale():
    title = 'How many earthquakes between {low} and {high} magnitude scale in recent {n} days'
    form = MagScaleForm()
    if form.validate_on_submit():
        recent_days = form.recent_days.data
        low = form.low_mag.data
        high = form.high_mag.data
        now = datetime.now()
        past = offset2datetime(now, recent_days)
        result = EarthquakeInfo.query.filter(
            (EarthquakeInfo.time >= past)
            & (EarthquakeInfo.time <= now)
            & (EarthquakeInfo.mag >= low)
            & (EarthquakeInfo.mag <= high)).all()
        return render_template('query.html',
                               title=title,
                               form=form,
                               result=result)
    return render_template('query.html', title=title, form=form)


@app.route('/compare', methods=['GET', 'POST'])
def compare():
    title = 'Are quakes more common within {distance} km of {location1} than {location2}'
    form = CompareForm()
    if form.validate_on_submit():
        loc1_latitude = form.loc1_latitude.data
        loc1_longitude = form.loc1_longitude.data
        loc2_latitude = form.loc2_latitude.data
        loc2_longitude = form.loc2_longitude.data
        distance = form.distance.data
        all_info = EarthquakeInfo.query.all()
        loc1_count = 0
        loc2_count = 0
        message = ''
        for info in all_info:
            if sphere_distance([loc1_latitude, loc1_longitude],
                               [info.latitude, info.longitude]) <= distance:
                loc1_count += 1
            if sphere_distance([loc2_latitude, loc2_longitude],
                               [info.latitude, info.longitude]) <= distance:
                loc2_count += 1
        if loc1_count > loc2_count:
            message = f'({loc1_latitude}, {loc1_longitude}) is more common, {loc1_count} earthquake(s)'
        elif loc1_count < loc2_count:
            message = f'({loc2_latitude}, {loc2_longitude}) is more common, {loc2_count} earthquake(s)'
        else:
            message = f'({loc1_latitude}, {loc1_longitude}) and ({loc2_latitude}, {loc2_longitude}) are equally common, {loc1_count} earthquake(s)'
        return render_template('query.html',
                               title=title,
                               form=form,
                               message=message)
    return render_template('query.html', title=title, form=form)


@app.route('/largest', methods=['GET', 'POST'])
def largest():
    title = 'The largest earthquake within {distance} of {where}'
    form = LargestForm()
    if form.validate_on_submit():
        distance = form.distance.data
        latitude = form.latitude.data
        longitude = form.longitude.data
        all_info = EarthquakeInfo.query.order_by(
            EarthquakeInfo.mag.desc()).all()
        for info in all_info:
            if sphere_distance([latitude, longitude],
                               [info.latitude, info.longitude]) <= distance:
                return render_template('query.html',
                                       title=title,
                                       form=form,
                                       result=[info])
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