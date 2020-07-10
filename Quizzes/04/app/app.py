"""Cloud Computing
Author: Bo Lin
Mav ID: 1001778270
Date: Jun/29/2020
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
app.config['port'] = int(os.getenv('PORT', '3463'))
app.config['SECRET_KEY'] = '1001778270'
app.config['allowed_csv_ext'] = {'csv', 'txt'}
app.config['project_dir'] = os.path.abspath(os.path.dirname(__file__))
app.config['upload_dir'] = os.path.join(app.config['project_dir'], 'assets')
app.config['db_path'] = os.path.join(app.config['upload_dir'], 'db.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + app.config['db_path']

db = SQLAlchemy(app)


class SmokeInfo(db.Model):
    id = db.Column(db.Integer,
                   nullable=False,
                   unique=True,
                   autoincrement=True,
                   primary_key=True)
    entity = db.Column(db.String(64))
    code = db.Column(db.String(5))
    year = db.Column(db.Integer)
    smokers = db.Column(db.Integer)


# form
class FileForm(FlaskForm):
    file = fields.FileField('Smokers Dataset File')
    submit = fields.SubmitField('Submit')


class PieForm(FlaskForm):
    entity = fields.StringField('Country Name')
    start = fields.IntegerField(
        'Start Year', validators=[validators.NumberRange(min=1980, max=2012)])
    end = fields.IntegerField(
        'End Year', validators=[validators.NumberRange(min=1980, max=2012)])
    submit = fields.SubmitField('Submit')


class BarForm(FlaskForm):
    entity = fields.StringField('Country Name')
    start = fields.IntegerField(
        'Start Year', validators=[validators.NumberRange(min=1980, max=2012)])
    end = fields.IntegerField(
        'End Year', validators=[validators.NumberRange(min=1980, max=2012)])
    submit = fields.SubmitField('Submit')


# router
@app.route('/', methods=['GET', 'POST'])
def index():
    title = 'Upload Smokers Dataset into Database'
    form = FileForm()
    if form.validate_on_submit():
        message = 'Upload Failed!'
        filename = secure_filename(form.file.data.filename)
        if utils.is_valid_ext(filename, app.config['allowed_csv_ext']):
            filename = os.path.join(app.config['upload_dir'], filename)
            form.file.data.save(filename)
            utils.insert_csv_to_db(filename, SmokeInfo, db)
            message = 'Upload Success!'
        return render_template('index.html',
                               title=title,
                               form=form,
                               message=message)
    return render_template('index.html', title=title, form=form)


@app.route('/pie_chart', methods=['GET', 'POST'])
def pie_chart():
    title = 'Pie Chart'
    form = PieForm()
    if form.validate_on_submit():
        entity = form.entity.data.title()
        start = form.start.data
        end = form.end.data
        label = []
        data = []
        for year in range(start, end + 1):
            label.append(str(year))
            result = SmokeInfo.query.filter((SmokeInfo.entity == entity)
                                            &
                                            (SmokeInfo.year == year)).first()
            data.append(result.smokers)
        viz = utils.get_viz('pie', label, data)
        return render_template('query.html',
                               title=title,
                               form=form,
                               viz=viz.render_embed(),
                               host=viz.js_host,
                               script_list=viz.js_dependencies.items)
    return render_template('query.html', title=title, form=form)


@app.route('/bar_chart', methods=['GET', 'POST'])
def bar_chart():
    title = 'Bar Chart'
    form = BarForm()
    if form.validate_on_submit():
        entity = form.entity.data.title()
        start = form.start.data
        end = form.end.data
        label = []
        data = []
        for year in range(start, end + 1):
            label.append(str(year))
            result = SmokeInfo.query.filter((SmokeInfo.entity == entity)
                                            &
                                            (SmokeInfo.year == year)).first()
            data.append(result.smokers)
        viz = utils.get_viz('bar', label, data)
        return render_template('query.html',
                               title=title,
                               form=form,
                               viz=viz.render_embed(),
                               host=viz.js_host,
                               script_list=viz.js_dependencies.items)
    return render_template('query.html', title=title, form=form)


@app.route('/scatter_chart', methods=['GET', 'POST'])
def scatter_chart():
    title = 'Scatter Chart'
    form = BarForm()
    if form.validate_on_submit():
        entity = form.entity.data.title()
        start = form.start.data
        end = form.end.data
        label = []
        data = []
        for year in range(start, end + 1):
            label.append(year)
            result = SmokeInfo.query.filter((SmokeInfo.entity == entity)
                                            &
                                            (SmokeInfo.year == year)).first()
            data.append(result.smokers)
        viz = utils.get_viz('scatter', label, data)
        return render_template('query.html',
                               title=title,
                               form=form,
                               viz=viz.render_embed(),
                               host=viz.js_host,
                               script_list=viz.js_dependencies.items)
    return render_template('query.html', title=title, form=form)


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