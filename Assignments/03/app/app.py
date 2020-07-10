"""flask app"""

import os
from time import time
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import fields, validators
from werkzeug.utils import secure_filename
import utils
from utils import TimeRecorder

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
time_rec = TimeRecorder()


# db entity
class CensusInfo(db.Model):
    id = db.Column(db.Integer,
                   nullable=False,
                   unique=True,
                   primary_key=True,
                   autoincrement=True)
    state_name = db.Column(db.String(25), nullable=False)
    county_name = db.Column(db.String(35), nullable=False)

for year in range(2010, 2020):
    setattr(CensusInfo, f'pop_est_{year}', db.Column(db.Integer,
                                                     nullable=False))


# form
class FileForm(FlaskForm):
    file = fields.FileField('CSV File')
    submit = fields.SubmitField('Submit')


class StateForm(FlaskForm):
    state_name = fields.StringField('State name or short name')
    submit = fields.SubmitField('Submit')


class CountyForm(FlaskForm):
    county_name = fields.StringField('County name')
    submit = fields.SubmitField('Submit')


class YearForm(FlaskForm):
    state_name = fields.StringField("State name or short name")
    start_year = fields.IntegerField(
        "Start Year", validators=[validators.NumberRange(min=2010, max=2019)])
    end_year = fields.IntegerField(
        "End Year", validators=[validators.NumberRange(min=2010, max=2019)])
    submit = fields.SubmitField("Submit")


# router
@app.route('/', methods=['GET', 'POST'])
def index():
    title = "Import data into Database"
    form = FileForm()
    if form.validate_on_submit():
        with time_rec.timer('Insert'):
            upload_status = 'failed'
            filename = secure_filename(form.file.data.filename)
            if utils.is_valid_ext(filename, app.config['allowed_csv_ext']):
                filename = os.path.join(app.config['upload_dir'], filename)
                form.file.data.save(filename)
                utils.insert_csv_to_db(filename, CensusInfo, db)
                upload_status = 'success'
        return render_template('index.html',
                               title=title,
                               form=form,
                               upload_status=upload_status)
    return render_template('index.html', title=title, form=form)


@app.route('/state', methods=['GET', 'POST'])
def state():
    title = 'State name or short name => Population'
    form = StateForm()
    if form.validate_on_submit():
        with time_rec.timer('Query by State Name'):
            state_name = form.state_name.data
            if state_name.upper() in utils.valid_short_name:
                state_name = utils.short2state[state_name.upper()]
            elif state_name.lower() in utils.valid_state_name:
                state_name = utils.lower2state[state_name.lower()]
            else:
                message = "No such state, please check it again."
                return render_template('query.html',
                                       title=title,
                                       form=form,
                                       message=message)
            result = CensusInfo.query.filter(
                CensusInfo.state_name == state_name).all()
        return render_template(
            'query.html',
            title=title,
            form=form,
            result=result,
            used_time=time_rec.get_records('Query by State Name'))
    return render_template('query.html', title=title, form=form)


@app.route('/county', methods=['GET', 'POST'])
def county():
    title = 'County name => Population'
    form = CountyForm()
    if form.validate_on_submit():
        with time_rec.timer('Query by County Name'):
            county_name = form.county_name.data.title() + " County"
            result = CensusInfo.query.filter(
                CensusInfo.county_name == county_name).all()
        return render_template(
            'query.html',
            title=title,
            form=form,
            result=result,
            used_time=time_rec.get_records('Query by County Name'))
    return render_template('query.html', title=title, form=form)


@app.route('/year', methods=['GET', 'POST'])
def year():
    title = 'State name and year range => Population'
    form = YearForm()
    if form.validate_on_submit():
        with time_rec.timer('Query by Year Range'):
            state_name = form.state_name.data
            start = form.start_year.data
            end = form.end_year.data
            if start > end:
                message = 'End Year should be greater than Start Year.'
                return render_template('year_query.html',
                                       title=title,
                                       form=form,
                                       message=message)
            if state_name.upper() in utils.valid_short_name:
                state_name = utils.short2state[state_name.upper()]
            elif state_name.lower() in utils.valid_state_name:
                state_name = utils.lower2state[state_name.lower()]
            else:
                message = "No such state, please check it again."
                return render_template('year_query.html',
                                       title=title,
                                       form=form,
                                       message=message)
            result = CensusInfo.query.filter(
                CensusInfo.state_name == state_name).all()
            year_range = [str(year) for year in range(start, end + 1)]
        return render_template(
            'year_query.html',
            title=title,
            form=form,
            result=result,
            year_range=year_range,
            used_time=time_rec.get_records('Query by Year Range'))
    return render_template('year_query.html', title=title, form=form)


@app.route('/timer', methods=['GET', 'POST'])
def timer():
    title = 'Timer'
    time_dict = time_rec.get_records()
    return render_template('timer.html', title=title, time_dict=time_dict)


@app.errorhandler(404)
@app.route('/error_404')
def page_not_found(error):
    return render_template('404.html', title='404')


@app.errorhandler(500)
@app.route('/error_500')
def requests_error(error):
    return render_template('500.html', title='500')


if __name__ == "__main__":
    utils.init_check(app.config['upload_dir'])
    db.create_all()
    app.run(host=app.config['host'], port=app.config['port'])