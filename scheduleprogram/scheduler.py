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


class AddModule(Form):
    user = StringField('Employee ID: ', validators=[DataRequired])
    modname = StringField('Module name: ', validators=[DataRequired])
    startdate = DateField('Starting date:', validators=[DataRequired()], format='%Y-%m-%d')
    projectID = IntegerField('Project ID:', validators=[DataRequired()])


class AddUser(Form):
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    access = IntegerField('access: (1:not vision, 2:vision, 3:edit', validators=[DataRequired()])


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(80))
    access = db.Column(db.Integer)

    def __init__(self, username, access, password):
        self.username = username
        self.access = access
        self.password = password


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(80), unique=True)
    project = db.Column(db.String(80), unique=True)
    startdate = db.Column(db.Date)

    # modules = db.Column(db.String(80))

    def __init__(self, project, startdate):
        # self.username = username
        self.project = project
        self.startdate = startdate

    def __repr__(self):
        return '<Project %r>' % self.project


class Modules(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80))
    modname = db.Column(db.String(80), unique=True)
    tasks = db.Column(db.String(80))
    # user_id = db.Column(db.String(80), db.ForeignKey('user.id)'))
    project_id = db.Column(db.Integer)
    startdate = db.Column(db.Date)

    def __init__(self, user, modname, startdate, project_id):
        self.user = user
        self.modname = modname
        self.startdate = startdate
        self.project_id = project_id


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    taskname = db.Column(db.String(120))
    duration = db.Column(db.Integer)
    state = db.Column(db.Integer)
    modules = db.Column(db.String(80))


@app.route('/initdb')
def page():
    db.create_all()
    # project = Project('test project', date(2015, 11, 15))
    # db.session.add(project)
    # db.session.commit()
    query = Project.query.order_by(Project.project)
    return render_template('display.html', output=query)


@app.route('/')
def homepage():
    query = Project.query.order_by(Project.project)
    return render_template('display.html', output=query)


@app.route('/users')
def listusers():
    query = User.query.order_by(User.username)
    return render_template('userlist.html', output=query)


@app.route('/cproject', methods=['GET', 'POST'])
def cproject():
    form = CreateProject()
    if form.validate_on_submit():
        projectname = form.name.data
        startdate = form.startdate.data
        project = Project(projectname, startdate)
        db.session.add(project)
        db.session.commit()
        flash('Project Created: ' + projectname)
        return redirect(url_for('homepage'))
    return render_template('cProject.html', form=form)


@app.route('/addmodule', methods=['GET', 'POST'])
def addmodule():
    form = AddModule()
    if form.validate_on_submit():
        user = form.user.data
        modname = form.modname.data
        startdate = form.startdate.data
        project_id = form.projectID.data
        module = Modules(user, modname, startdate, project_id)
        db.session.add(module)
        db.session.comit()
        flash('Module Added' + module.modname)
        return redirect(url_for('homepage'))
    return render_template('addModule.html', form=form)


@app.route('/adduser', methods=['GET', 'POST'])
def adduser():
    form = AddUser()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        access = form.access.data
        user = User(username, password, access)
        db.session.add(user)
        db.session.commit()
        flash('Added User: ' + username)
        return redirect(url_for('listusers'))
    return render_template('addUser.html', form=form)


if __name__ == '__main__':
    app.run()
