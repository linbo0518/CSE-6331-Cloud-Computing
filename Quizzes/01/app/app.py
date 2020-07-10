import os
import sys
import pandas as pd
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
# from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_bootstrap import Bootstrap
from wtforms import StringField, IntegerField, SubmitField, SelectField, FileField
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
    name = db.Column(db.String(20),
                     unique=True,
                     nullable=False,
                     primary_key=True)
    id = db.Column(db.Integer, nullable=True)
    room = db.Column(db.Integer, nullable=True)
    state = db.Column(db.String(2), nullable=True)
    picture = db.Column(db.String(20), nullable=True)
    caption = db.Column(db.String(100), nullable=True)


class NameForm(FlaskForm):
    name = StringField('Name')
    submit = SubmitField('Submit')


class UploadForm(FlaskForm):
    upload_file = FileField('File')
    submit = SubmitField('Submit')


class Query1Form(FlaskForm):
    low = IntegerField('Minimum Room', validators=[Optional()])
    high = IntegerField('Maximum Room', validators=[Optional()])
    submit = SubmitField('Search')


class Query2Form(FlaskForm):
    search_category = SelectField('Search by',
                                  choices=[('id', 'ID'), ('room', 'Room')])
    data = IntegerField('Data')
    category = SelectField('Attribute',
                           choices=[('name', 'Name'), ('picture', 'Picture')])
    modified = StringField('Change to')
    image = FileField('Change image')
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
                   id=row['ID'],
                   room=row['Room'],
                   state=row['State'],
                   picture=row['Picture'],
                   caption=row['Caption']))
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
        message = ''
        try:
            number = int(name)
            if (number % 2 == 0):
                message = 'Even'
            else:
                message = 'Odd'
        except:
            message = 'Not Known'
        return render_template('index.html',
                               form=form,
                               name=name,
                               message=message,
                               image_name='c.png')
    return render_template('index.html',
                           form=form,
                           name=None,
                           image_name='c.png')


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


@app.route('/query1', methods=['GET', 'POST'])
def query1():
    form = Query1Form()
    if form.validate_on_submit():
        low = form.low.data
        high = form.high.data
        if low is None and high is not None:
            result = Entity.query.filter(Entity.room < high).all()
        elif low is not None and high is None:
            result = Entity.query.filter(Entity.room > low).all()
        elif low is not None and high is not None:
            result = Entity.query.filter((Entity.room > low)
                                         & (Entity.room < high)).all()
        else:
            result = Entity.query.all()
        result = check_image_file_exist(result)
        return render_template('query2.html', form=form, result=result)
    return render_template('query1.html', form=form)


@app.route('/query2', methods=['GET', 'POST'])
def query2():
    form = Query2Form()
    if form.validate_on_submit():
        search_category = form.search_category.data
        data = form.data.data
        category = form.category.data
        modified = form.modified.data
        filename = secure_filename(form.image.data.filename)
        if search_category == 'id':
            result = Entity.query.filter_by(id=data).all()
        elif search_category == 'room':
            result = Entity.query.filter_by(room=data).all()
        else:
            pass
        if (len(result) == 1):
            if category == 'name':
                setattr(result[0], category, modified)
                db.session.commit()
                message = 'Modified success'
                result = check_image_file_exist(result)
            elif category == 'picture':
                if is_valid_ext(filename, app.config['allowed_image_ext']):
                    form.image.data.save(os.path.join(app.config['image_upload_dir'], filename))
                    result[0].picture = filename
                    db.session.commit()
                    message = "Modified success"
                else:
                    message = "Modified failed"
            return render_template('query2.html',
                                form=form,
                                result=result,
                                message=message)
        else:
            message = 'No result or multiple result'
            result = check_image_file_exist(result)
            return render_template('query2.html',
                                   form=form,
                                   result=result,
                                   message=message)
    return render_template('query2.html', form=form)


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
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    app.run(host=app.config['host'], port=app.config['port'])