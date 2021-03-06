"""Cloud Computing
Author: Bo Lin
Mav ID: 1001778270
Date: Jun/28/2020
"""

import os
from datetime import datetime
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import fields, validators
from werkzeug.utils import secure_filename

import utils

app = Flask(__name__, static_folder='assets')
Bootstrap(app)

# config
app.config['host'] = '0.0.0.0'
app.config['port'] = int(os.getenv('PORT', '80'))
app.config['SECRET_KEY'] = '1001778270'
app.config['allowed_csv_ext'] = {'csv', 'txt'}
app.config['project_dir'] = os.path.abspath(os.path.dirname(__file__))
app.config['upload_dir'] = os.path.join(app.config['project_dir'], 'assets')
app.config['db_path'] = os.path.join(app.config['upload_dir'], 'db.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + app.config['db_path']

db = SQLAlchemy(app)
time_rec = utils.TimeRecorder()


# database entity
class EarthquakeInfo(db.Model):
    time = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    depth = db.Column(db.Float, nullable=True)
    mag = db.Column(db.Float, nullable=True)
    magType = db.Column(db.String(10), nullable=True)
    nst = db.Column(db.Integer, nullable=True)
    gap = db.Column(db.Float, nullable=True)
    dmin = db.Column(db.Float, nullable=True)
    rms = db.Column(db.Float, nullable=True)
    net = db.Column(db.String(5), nullable=True)
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
    file = fields.FileField('Earthquake Dataset File')
    submit = fields.SubmitField('Submit')


class StatForm(FlaskForm):
    low = fields.IntegerField(
        'Low Magnitude', validators=[validators.NumberRange(min=0, max=8)])
    high = fields.IntegerField(
        'High Magnitude', validators=[validators.NumberRange(min=0, max=8)])
    method = fields.SelectField('Visualization Method',
                                choices=[('bar', 'Bar'), ('pie', 'Pie')])
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
    method = fields.SelectField('Visualization Method',
                                choices=[('bar', 'Bar'), ('pie', 'Pie')])
    submit = fields.SubmitField('Submit')


# router
@app.route('/', methods=['GET', 'POST'])
def index():
    title = 'Upload Earthquake Dataset into Database'
    form = FileForm()
    if form.validate_on_submit():
        time_key = datetime.now().ctime() + ' - ' + title
        message = 'Upload Failed!'
        with time_rec.timer(time_key):
            filename = secure_filename(form.file.data.filename)
            if utils.is_valid_ext(filename, app.config['allowed_csv_ext']):
                filename = os.path.join(app.config['upload_dir'], filename)
                form.file.data.save(filename)
                utils.insert_csv_to_db(filename, EarthquakeInfo, db)
                message = 'Upload Success!'
        used_time = time_rec.get_records(time_key)
        return render_template('index.html',
                               title=title,
                               form=form,
                               message=message,
                               used_time=used_time)
    return render_template('index.html', title=title, form=form)


@app.route('/stat', methods=['GET', 'POST'])
def stat():
    title = 'Data Visualization of Magnitude'
    form = StatForm()
    if form.validate_on_submit():
        time_key = datetime.now().ctime() + ' - ' + title
        with time_rec.timer(time_key):
            low = form.low.data
            high = form.high.data
            method = form.method.data
            label = []
            data = []
            for i in range(low, high):
                label.append(f'{i} - {i + 1}')
                result = EarthquakeInfo.query.filter(
                    (EarthquakeInfo.mag >= i)
                    & (EarthquakeInfo.mag < i + 1)).all()
                data.append(len(result))
            viz = utils.get_viz(method, label, data)
        return render_template('query.html',
                               title=title,
                               form=form,
                               viz=viz.render_embed(),
                               host=viz.js_host,
                               script_list=viz.js_dependencies.items)
    return render_template('query.html', title=title, form=form)


@app.route('/compare', methods=['GET', 'POST'])
def compare():
    title = 'Data Visualization of Compare'
    form = CompareForm()
    if form.validate_on_submit():
        time_key = datetime.now().ctime() + ' - ' + title
        with time_rec.timer(time_key):
            loc1_lat = form.loc1_latitude.data
            loc1_long = form.loc1_longitude.data
            loc2_lat = form.loc2_latitude.data
            loc2_long = form.loc2_longitude.data
            distance = form.distance.data
            method = form.method.data
            all_info = EarthquakeInfo.query.all()
            loc1_count = 0
            loc2_count = 0
            for info in all_info:
                if utils.sphere_distance(
                    [loc1_lat, loc1_long],
                    [info.latitude, info.longitude]) <= distance:
                    loc1_count += 1
                if utils.sphere_distance(
                    [loc2_lat, loc2_long],
                    [info.latitude, info.longitude]) <= distance:
                    loc2_count += 1
            label = ['Location1', 'Location2']
            data = [loc1_count, loc2_count]
            viz = utils.get_viz(method, label, data)
        return render_template('query.html',
                               title=title,
                               form=form,
                               viz=viz.render_embed(),
                               host=viz.js_host,
                               script_list=viz.js_dependencies.items)
    return render_template('query.html', title=title, form=form)


@app.route('/timer', methods=['GET', 'POST'])
def timer():
    title = 'Time Log'
    time_recordings = time_rec.get_records()
    return render_template('timer.html',
                           title=title,
                           time_recordings=time_recordings)


@app.errorhandler(404)
@app.route('/error_404')
def page_not_found(error):
    return render_template('404.html', title='404')


@app.errorhandler(500)
@app.route('/error_500')
def requests_error(error):
    return render_template('500.html', title='500')


#main
if __name__ == '__main__':
    utils.init_check(app.config['upload_dir'])
    db.create_all()
    app.run(host=app.config['host'], port=app.config['port'])