import os
import sys
import pandas as pd
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, IntegerField, SubmitField, SelectField, FileField, Form
from wtforms.validators import DataRequired, Optional
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder='assets/image')
bootstrap = Bootstrap(app)

### config ###
app.config['host'] = '0.0.0.0'
app.config['port'] = int(os.getenv('PORT', '3463'))
app.config['SECRET_KEY'] = '1001778270'
app.config['allowed_csv_ext'] = {'csv', 'txt'}
app.config['allowed_image_ext'] = {'jpg', 'jpeg', 'png'}
app.config['project_dir'] = os.path.abspath(os.path.dirname(__file__))
app.config['upload_base_dir'] = os.path.join(app.config['project_dir'],
                                             'assets')
app.config['csv_upload_dir'] = os.path.join(app.config['upload_base_dir'],
                                            'csv')
app.config['image_upload_dir'] = os.path.join(app.config['upload_base_dir'],
                                              'image')
app.config['database_path'] = os.path.join(app.config['upload_base_dir'],
                                           'database.sqlite')
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + app.config['database_path']
db = SQLAlchemy(app)


### helper function ###
class Entity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    salary = db.Column(db.Integer, nullable=True)
    room = db.Column(db.Integer, nullable=True)
    telnum = db.Column(db.Integer, nullable=True)
    picture = db.Column(db.String(20), nullable=True)
    keywords = db.Column(db.String(100), nullable=True)


class NameForm(FlaskForm):
    name = StringField('Name')
    submit = SubmitField('Submit')


class UploadForm(FlaskForm):
    upload_file = FileField('File')
    submit = SubmitField('Submit')


class Query1Form(FlaskForm):
    name = StringField('Name')
    submit = SubmitField('Search')


class Query2Form(FlaskForm):
    low = IntegerField('Low salary', validators=[Optional()])
    high = IntegerField('High salary', validators=[Optional()])
    submit = SubmitField('Search')


class Query3Form(FlaskForm):
    name = StringField('Name')
    upload_file = FileField('Image')
    confirm = SubmitField('Confirm')


class Query4Form(FlaskForm):
    name = StringField('Name')
    submit = SubmitField('Delete')


class Query5Form(FlaskForm):
    name = StringField('Name')
    category = SelectField('Attribute',
                           choices=[
                               ('salary', 'Salary'),
                               ('room', 'Room'),
                               ('telnum', 'Telnum'),
                               ('picture', 'Picture'),
                               ('keywords', 'Keywords'),
                           ])
    modified = StringField('Change to')
    submit = SubmitField('Submit')


def init_check():
    paths = [
        app.config['upload_base_dir'],
        app.config['csv_upload_dir'],
        app.config['image_upload_dir'],
    ]
    for path in paths:
        if not os.path.exists(path):
            os.mkdir(path)


def is_valid_ext(filename, allowed_ext=None):
    if allowed_ext is None:
        return True
    _, ext = os.path.splitext(filename)
    return ext[1:] in allowed_ext


def _csv2entity_list(csv_filename):
    entity_list = []
    df = pd.read_csv(csv_filename, skipinitialspace=True)
    for _, row in df.iterrows():
        entity_list.append(
            Entity(name=row['Name'],
                   salary=row['Salary'],
                   room=row['Room'],
                   telnum=row['Telnum'],
                   picture=row['Picture'],
                   keywords=row['Keywords']))
    return entity_list


def _insert_entity_to_db(entity_list):
    for entity in entity_list:
        result = Entity.query.filter_by(name=entity.name).first()
        if result:
            result = entity
        else:
            db.session.add(entity)
    db.session.commit()


def insert_csv_to_db(csv_filename):
    entity_list = _csv2entity_list(csv_filename)
    _insert_entity_to_db(entity_list)


def check_image_file_exist(result):
    for entity in result:
        if entity.picture:
            if not os.path.exists(
                    os.path.join(app.config['image_upload_dir'],
                                 entity.picture)):
                entity.picture = None
    return result


### router ###
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        return render_template('index.html', form=form, name=name)
    return render_template('index.html', form=form, name=None)


@app.route('/upload_csv', methods=['GET', 'POST'])
def upload_csv():
    form = UploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.upload_file.data.filename)
        if is_valid_ext(filename, app.config['allowed_csv_ext']):
            filename = os.path.join(app.config['csv_upload_dir'], filename)
            form.upload_file.data.save(filename)
            insert_csv_to_db(filename)
            return render_template('index.html',
                                   form=form,
                                   upload_status="success")
        else:
            return render_template('index.html',
                                   form=form,
                                   upload_status="failed")
    return render_template('index.html', form=form, upload_status=None)


@app.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    form = UploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.upload_file.data.filename)
        if is_valid_ext(filename, app.config['allowed_image_ext']):
            form.upload_file.data.save(
                os.path.join(app.config['image_upload_dir'], filename))
            return render_template('index.html',
                                   form=form,
                                   upload_status="success")
        else:
            return render_template('index.html',
                                   form=form,
                                   upload_status="failed")
    return render_template('index.html', form=form, upload_status=None)


@app.route('/show_upload')
def show_upload():
    csv_files = os.listdir(app.config['csv_upload_dir'])
    image_files = os.listdir(app.config['image_upload_dir'])
    return render_template('show_upload.html',
                           csv_files=csv_files,
                           image_files=image_files)


@app.route('/search_by_name', methods=['GET', 'POST'])
def search_by_name():
    form = Query1Form()
    if form.validate_on_submit():
        name = form.name.data
        result = Entity.query.filter_by(name=name).all()
        result = check_image_file_exist(result)
        return render_template('query1.html', form=form, result=result)
    return render_template('query1.html', form=form)


@app.route('/search_by_salary', methods=['GET', 'POST'])
def search_by_salary():
    form = Query2Form()
    if form.validate_on_submit():
        low = form.low.data
        high = form.high.data
        if low is None and high is not None:
            result = Entity.query.filter(Entity.salary < high).all()
        elif low is not None and high is None:
            result = Entity.query.filter(Entity.salary > low).all()
        elif low is not None and high is not None:
            result = Entity.query.filter((Entity.salary > low)
                                         & (Entity.salary < high)).all()
        else:
            result = Entity.query.all()
        result = check_image_file_exist(result)
        return render_template('query2.html', form=form, result=result)
    return render_template('query2.html', form=form)


@app.route('/add_picture', methods=['GET', 'POST'])
def add_picture():
    form = Query3Form()
    if form.validate_on_submit():
        name = form.name.data
        result = Entity.query.filter_by(name=name).all()
        if (len(result) == 1):
            filename = secure_filename(form.upload_file.data.filename)
            if is_valid_ext(filename, app.config['allowed_image_ext']):
                form.upload_file.data.save(
                    os.path.join(app.config['image_upload_dir'], filename))
                result[0].picture = filename
                db.session.commit()
                message = "Modify success"
                return render_template('query3.html',
                                       form=form,
                                       result=result,
                                       message=message)
            else:
                message = "Modify failed"
                return render_template('query3.html',
                                       form=form,
                                       result=result,
                                       message=message)
        else:
            message = "No result"
            result = check_image_file_exist(result)
            return render_template('query3.html',
                                   form=form,
                                   result=result,
                                   message=message)

    return render_template('query3.html', form=form)


@app.route('/remove_data', methods=['GET', 'POST'])
def remove_data():
    form = Query4Form()
    if form.validate_on_submit():
        name = form.name.data
        result = Entity.query.filter_by(name=name).all()
        if (len(result) == 1):
            db.session.delete(result[0])
            db.session.commit()
            message = 'Delete success'
            result = check_image_file_exist(result)
            return render_template('query4.html',
                                   form=form,
                                   result=result,
                                   message=message)
        else:
            message = 'No result'
            result = check_image_file_exist(result)
            return render_template('query4.html',
                                   form=form,
                                   result=result,
                                   message=message)
    return render_template('query4.html', form=form)


@app.route('/modify_data', methods=['GET', 'POST'])
def modify_data():
    form = Query5Form()
    if form.validate_on_submit():
        name = form.name.data
        category = form.category.data
        modified = form.modified.data
        result = Entity.query.filter_by(name=name).all()
        if (len(result) == 1):
            setattr(result[0], category, modified)
            db.session.commit()
            message = 'Modified success'
            result = check_image_file_exist(result)
            return render_template('query5.html',
                                   form=form,
                                   result=result,
                                   message=message)
        else:
            message = 'No result'
            result = check_image_file_exist(result)
            return render_template('query5.html',
                                   form=form,
                                   result=result,
                                   message=message)
    return render_template('query5.html', form=form)


@app.route('/help')
def help():
    text_list = []
    # Python Version
    text_list.append({'label': 'Python Version', 'value': str(sys.version)})
    # os.path.abspath(os.path.dirname(__file__))
    text_list.append({
        'label': 'os.path.abspath(os.path.dirname(__file__))',
        'value': str(os.path.abspath(os.path.dirname(__file__)))
    })
    # OS Current Working Directory
    text_list.append({'label': 'OS CWD', 'value': str(os.getcwd())})
    # OS CWD Contents
    label = 'OS CWD Contents'
    value = ''
    text_list.append({'label': label, 'value': value})
    return render_template('help.html', text_list=text_list, title='help')


@app.errorhandler(404)
@app.route('/error404')
def page_not_found(error):
    return render_template('404.html', title='404')


@app.errorhandler(500)
@app.route('/error500')
def requests_error(error):
    return render_template('500.html', title='500')


if __name__ == '__main__':
    init_check()
    db.create_all()
    app.run(host=app.config['host'], port=app.config['port'])