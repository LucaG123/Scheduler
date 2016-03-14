# all the imports
from flask import Flask, render_template, flash, url_for, redirect, request
# imports the library for connecting Python to SQLite
# configuration
from flask.ext.sqlalchemy import SQLAlchemy  # library to more easily manipulate database

from flask_wtf import Form
from wtforms import StringField, DateField, PasswordField, IntegerField, SelectField, HiddenField
from wtforms.validators import DataRequired  # imports different kinds of form fields

DATABASE = "database.db"
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# creates the application
app = Flask(__name__)
app.config.from_object(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # sets the database location when created
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)  # init the database


class EditTask(Form):  # create the form for Edit Task button
    name = StringField('Rename:')
    # the columns in the data base being commited when respective form is submitted. StringField
    # only accepts a String and so on for other variable types like Integer and Date
    duration = IntegerField('Duration:')
    state = IntegerField('State:')
    task_id = HiddenField('Task ID')  # HiddenField doesn't show a field on the form;
    #  it has to be filled by other means
    # validators checks to make sure the user put
    # the correct date type in the field in the form


class AddTask(Form):  # create the form for Add Task button
    name = StringField('Task:', validators=[DataRequired()])
    module_id = SelectField('Module:', coerce=int, validators=[DataRequired()])
    duration = IntegerField('Duration:', validators=[DataRequired()])


class AddProject(Form):  # create the form for Add Project button
    name = StringField('Name of project:', validators=[DataRequired()])
    startdate = DateField('Starting date:', validators=[DataRequired()], format='%Y-%m-%d')


class AddModule(Form):  # create the form for Add Module button
    user = SelectField('Employee: ', validators=[DataRequired()])
    name = StringField('Module name: ', validators=[DataRequired()])
    startdate = DateField('Starting date:', validators=[DataRequired()], format='%Y-%m-%d')
    project = SelectField('Project:', coerce=int, validators=[DataRequired()])


class AddUser(Form):  # create the form for Add User button
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    access = IntegerField('Access: (1:not vision, 2:vision, 3:edit)', validators=[DataRequired()])


class User(db.Model):  # creates the user database
    id = db.Column(db.Integer, primary_key=True)  # creates a column in the database.
    """Primary_key creates a unique ID for each item in the database. In this context, it is used
    to order them when creating lists"""
    username = db.Column(db.String(40), unique=True)
    """unique prevents the database from adding two items in the database with the same name.
    In this contest, it prevents multiple users to have the same name"""
    password = db.Column(db.String(80))
    access = db.Column(db.Integer)  # determines what is visible to the user

    def __init__(self, username, access, password):  # initializes the database.
        self.username = username
        self.access = access
        self.password = password


class Project(db.Model):  # creates the project database
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    startdate = db.Column(db.Date)
    modules = db.relationship('Modules', backref='proj')  # creates a relationship between Project and Modules

    def __init__(self, name, startdate):
        self.name = name
        self.startdate = startdate

    def __repr__(self):
        return '<Project %r>' % self.name


class Modules(db.Model):  # creates the module database
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80))
    name = db.Column(db.String(80))
    tasks = db.relationship('Tasks', backref='module')
    # user_id = db.Column(db.String(80), db.ForeignKey('user.id)'))
    project = db.Column(db.Integer, db.ForeignKey('project.id'))
    startdate = db.Column(db.Date)

    def __init__(self, user, name, startdate, project):
        self.user = user
        self.name = name
        self.startdate = startdate
        self.project = project


class Tasks(db.Model):  # creates the task database
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'))
    name = db.Column(db.String(200))
    duration = db.Column(db.Integer, default=0)
    state = db.Column(db.Integer, default=0)

    def __init__(self, name, module_id, duration):
        self.name = name
        self.module_id = module_id
        self.duration = duration


@app.route('/')
def page():
    db.create_all()
    # project = Project('test project', date(2015, 11, 15))
    # db.session.add(project)
    # db.session.commit()
    query = Project.query.options(
            db.subqueryload_all(
                    Project.modules,
                    Modules.tasks
            )
    ).all()
    return render_template('display.html', output=query)


@app.route('/display')
def homepage():

    query = Project.query.order_by(Project.name)
    return render_template('display.html', output=query)


'''@app.route('/users')
def listusers():
    query = User.query.order_by(User.username)
    return render_template('userlist.html', output=query)'''


@app.route('/addproject', methods=['GET', 'POST'])
def addproject():
    form = AddProject()
    if form.validate_on_submit():
        projectname = form.name.data
        startdate = form.startdate.data
        project = Project(projectname, startdate)
        db.session.add(project)
        db.session.commit()
        flash('Project Added: ' + projectname)
        return redirect(url_for('homepage'))
    return render_template('addProject.html', form=form)


@app.route('/addmodule', methods=['GET', 'POST'])
def addmodule():
    form = AddModule()
    form.user.choices = [(user.username, user.username) for user in User.query.all()]
    form.project.choices = [(project.id, project.name) for project in Project.query.all()]
    if form.validate_on_submit():
        user = form.user.data
        name = form.name.data
        startdate = form.startdate.data
        project = form.project.data
        module = Modules(user, name, startdate, project)
        db.session.add(module)
        db.session.commit()
        flash('Added Module: ' + module.name)
        return redirect(url_for('homepage'))
    return render_template('addModule.html', form=form)


# query = Model.query.filter_by(column="data").first()
# query._columnthatyouaremodifying_ = "data"
# db.session.add(query); db.session.commit()

@app.route('/adduser', methods=['GET', 'POST'])
def adduser():
    form = AddUser()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        access = form.access.data
        user = User(username, access, password)
        db.session.add(user)
        db.session.commit()
        flash('Added User: ' + username)
        return redirect(url_for('homepage'))
    return render_template('addUser.html', form=form)


@app.route('/addtask', methods=['GET', 'POST'])
def addtask():
    form = AddTask()
    form.module_id.choices = [(module.id, module.name) for module in Modules.query.all()]
    if form.validate_on_submit():
        module_id = form.module_id.data
        dur = form.duration.data
        name = form.name.data
        task = Tasks(name, module_id, dur)
        db.session.add(task)
        db.session.commit()
        flash('Added Task: ' + form.name.data)
        return redirect(url_for('homepage'))
    return render_template('addTask.html', form=form)


@app.route('/editTask', methods=['GET', 'POST'])
def edittask():
    form = EditTask()
    if form.validate_on_submit():
        flash('Task Edited')
        query = Tasks.query.filter_by(id=int(form.task_id.data)).first()
        query.name = form.name.data
        query.duration = form.duration.data
        query.state = form.state.data
        db.session.add(query)
        db.session.commit()
        return redirect(url_for('homepage'))
    elif request.args.get('task'):
        form.task_id.data = request.args.get('task')
        return render_template('editTask.html', form=form)
    else:
        for error in form.errors:
            flash('Field not filled out: ' + error)
        flash('No task to edit')
        return redirect(url_for('homepage'))

if __name__ == '__main__':
    app.run(None, 8001)
