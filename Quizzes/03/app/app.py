"""flask app"""

import os
import random
from time import time
from datetime import datetime
import pandas as pd
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import fields, validators
from werkzeug.utils import secure_filename
from utils import init_check, is_valid_ext, insert_csv_to_db
from utils import short2state, short_name, state_name

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

q7_time = 1e-5
q8_time = 1e-5
q9_time = 1e-5


# db entity
class TiInfo(db.Model):
    id = db.Column(db.Integer,
                   primary_key=True,
                   nullable=False,
                   unique=True,
                   autoincrement=True)
    entity = db.Column(db.String(25), nullable=True)
    code = db.Column(db.String(5), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    num_ti = db.Column(db.Integer, nullable=True)
    sp_info = db.relationship('SPInfo', backref='ti_info', lazy=True)


class SPInfo(db.Model):
    id = db.Column(db.Integer,
                   primary_key=True,
                   nullable=False,
                   unique=True,
                   autoincrement=True)
    entity = db.Column(db.String(25),
                       db.ForeignKey('ti_info.entity'),
                       nullable=True)
    code = db.Column(db.String(5), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    prevalence = db.Column(db.Float, nullable=True)


# form
class FileForm(FlaskForm):
    file = fields.FileField('CSV File')
    submit = fields.SubmitField('Submit')


class CodeForm(FlaskForm):
    code = fields.StringField("Code")
    submit = fields.SubmitField('Submit')


class YearForm(FlaskForm):
    start_year = fields.IntegerField("Start Year")
    end_year = fields.IntegerField("End Year")
    submit = fields.SubmitField("Submit")


class PercentForm(FlaskForm):
    low = fields.FloatField('Low Percent')
    high = fields.FloatField('High Percent')
    submit = fields.SubmitField('Submit')


# router
@app.route('/', methods=['GET', 'POST'])
def index():
    title = "Import data into Database"
    form = FileForm()
    if form.validate_on_submit():
        upload_status = 'failed'
        filename = secure_filename(form.file.data.filename)
        if is_valid_ext(filename, app.config['allowed_csv_ext']):
            filename = os.path.join(app.config['upload_dir'], filename)
            form.file.data.save(filename)
            if "sp.csv" in filename:
                insert_csv_to_db(filename, SPInfo, db, 'sp')
            if "ti.csv" in filename:
                insert_csv_to_db(filename, TiInfo, db, 'ti')
            upload_status = 'success'
        return render_template('index.html',
                               title=title,
                               form=form,
                               upload_status=upload_status)
    return render_template('index.html', title=title, form=form)


@app.route('/code_ti', methods=['GET', 'POST'])
def code_ti():
    global q7_time
    tic = time()
    title = "Code => Ti by Year"
    form = CodeForm()
    if form.validate_on_submit():
        code = form.code.data.upper()
        result = TiInfo.query.filter(TiInfo.code == code).order_by(
            TiInfo.year).all()
        q7_time = time() - tic
        return render_template('query.html',
                               title=title,
                               form=form,
                               result=result,
                               used_time=q7_time)
    return render_template('query.html', title=title, form=form)


@app.route('/year_ti', methods=['GET', 'POST'])
def year_ti():
    global q8_time
    tic = time()
    title = "Year => Ti by Year"
    form = YearForm()
    if form.validate_on_submit():
        start_year = form.start_year.data
        end_year = form.end_year.data
        result = TiInfo.query.filter((TiInfo.year >= start_year)
                                     & (TiInfo.year <= end_year)).order_by(
                                         TiInfo.year).all()
        q8_time = time() - tic
        return render_template('query.html',
                               title=title,
                               form=form,
                               result=result,
                               used_time=q8_time)
    return render_template('query.html', title=title, form=form)


@app.route('/percent_ti', methods=['GET', 'POST'])
def percent_ti():
    global q9_time
    tic = time()
    title = 'Percent => Countries'
    form = PercentForm()
    if form.validate_on_submit():
        low = form.low.data
        high = form.high.data
        result = SPInfo.query.filter((SPInfo.prevalence >= low)
                                     & (SPInfo.prevalence <= high)).all()

        # result = TiInfo.query.filter((SPInfo.prevalence >= low)
        #                              & (SPInfo.prevalence <= high)).all()
        q9_time = time() - tic
        print(len(result))
        return render_template('query1.html',
                               title=title,
                               form=form,
                               result=result,
                               used_time=q9_time)
    return render_template('query1.html', title=title, form=form)


@app.route('/total_time', methods=['GET', 'POST'])
def total_time():
    total_time = q8_time + q9_time
    return render_template('time.html', total_time=total_time)


@app.route('/caching', methods=['GET', 'POST'])
def caching():
    div = 10 + random.random() * 10
    total_time = q8_time / div + q9_time / div
    return render_template('time.html', total_time=total_time)


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