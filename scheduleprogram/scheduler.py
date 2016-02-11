# all the imports
from flask import Flask, render_template, flash, url_for, redirect

# configuration
from flask.ext.sqlalchemy import SQLAlchemy

from flask_wtf import Form
from wtforms import StringField, DateField, PasswordField, IntegerField
from wtforms.validators import DataRequired

DATABASE = "database.db"
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class CreateProject(Form):
    name = StringField('Name of project:', validators=[DataRequired()])
    startdate = DateField('Starting date:', validators=[DataRequired()], format='%Y-%m-%d')
    enddate = DateField('Ending date:', validators=[DataRequired()], format='%Y-%m-%d')


class AddUser(Form):
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    access = IntegerField('access: (1:not vision, 2:vision, 3:edit', validators=[DataRequired()])


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(80))
    access = db.Column(db.Integer)

    def __init__(self, username, access):
        self.username
        self.access


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(80), unique=True)
    project = db.Column(db.String(80), unique=True)
    startdate = db.Column(db.Date)
    enddate = db.Column(db.Date)
    modules = db.relationship('Modules')

    def __init__(self, project, startdate, enddate):
        # self.username = username
        self.project = project
        self.startdate = startdate
        self.enddate = enddate

    def __repr__(self):
        return '<Project %r>' % self.project


class Modules(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modulename = db.Column(db.String(80), unique=True)
    tasks = db.relationship("Tasks")
    user_id = db.Column(db.String(80), db.ForeignKey('user.id)'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    def __init__(self, modulename):
        self.modulename = modulename


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    taskname = db.Column(db.String(120))
    duration = db.Column(db.Integer)
    modules_id = db.Column(db.Integer, db.ForeignKey('modules.id'))


@app.route('/initdb')
def page():
    db.create_all()
    # project = Project('test project', date(2015, 11, 15), date(2016, 11, 16))
    # db.session.add(project)
    # db.session.commit()
    query = Project.query.order_by(Project.project)
    return render_template('display.html', output=query)


@app.route('/')
def homepage():
    query = Project.query.order_by(Project.project)
    return render_template('display.html', output=query)


@app.route('/cproject', methods=['GET', 'POST'])
def cproject():
    form = CreateProject()
    if form.validate_on_submit():
        projectname = form.name.data
        startdate = form.startdate.data
        enddate = form.enddate.data
        project = Project(projectname, startdate, enddate)
        db.session.add(project)
        db.session.commit()
        flash('Project Created: ' + projectname)
        return redirect(url_for('homepage'))
    return render_template('cProject.html', form=form)


@app.route('/addUser', methods=['GET', 'POST'])
def adduser():
    form = AddUser()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        access = form.access.data
        user = User(username, password, access)
        db.session.add(user)
        db.session.commit()


if __name__ == '__main__':
    app.run()
