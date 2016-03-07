# all the imports
from flask import Flask, render_template, flash, url_for, redirect, request
# configuration
from flask.ext.sqlalchemy import SQLAlchemy

from flask_wtf import Form
from wtforms import StringField, DateField, PasswordField, IntegerField, SelectField, HiddenField
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
move = 10


class EditTask(Form):
    duration = IntegerField('Duration:', validators=[DataRequired()])
    state = IntegerField('State:', validators=[DataRequired()])
    task_id = HiddenField('Task ID', validators=[DataRequired()])

class AddTask(Form):
    name = StringField('Task:', validators=[DataRequired()])
    module_id = SelectField('Module:', coerce=int, validators=[DataRequired()])
    duration = IntegerField('Duration:', validators=[DataRequired()])


class AddProject(Form):
    name = StringField('Name of project:', validators=[DataRequired()])
    startdate = DateField('Starting date:', validators=[DataRequired()], format='%Y-%m-%d')


class AddModule(Form):
    user = SelectField('Employee: ', validators=[DataRequired()])
    name = StringField('Module name: ', validators=[DataRequired()])
    startdate = DateField('Starting date:', validators=[DataRequired()], format='%Y-%m-%d')
    project = SelectField('Project:', coerce=int, validators=[DataRequired()])


class AddUser(Form):
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    access = IntegerField('Access: (1:not vision, 2:vision, 3:edit)', validators=[DataRequired()])


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
    name = db.Column(db.String(80), unique=True)
    startdate = db.Column(db.Date)
    modules = db.relationship('Modules', backref='proj')

    def __init__(self, name, startdate):
        # self.username = username
        self.name = name
        self.startdate = startdate

    def __repr__(self):
        return '<Project %r>' % self.name


class Modules(db.Model):
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


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'))
    name = db.Column(db.String(200))
    duration = db.Column(db.Integer, default=0)
    state = db.Column(db.Integer, default=0)

    def __init__(self, name, module_id, duration):
        self.name = name
        self.module_id = module_id
        self.duration = duration


@app.route('/initdb')
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


@app.route('/')
def homepage():
    query = Project.query.order_by(Project.name)
    return render_template('display.html', output=query)


@app.route('/users')
def listusers():
    query = User.query.order_by(User.username)
    return render_template('userlist.html', output=query)


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
        user = User(username, password, access)
        db.session.add(user)
        db.session.commit()
        flash('Added User: ' + username)
        return redirect(url_for('listusers'))
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
    if request.args.get('task') is not None:
        form = EditTask()
        task = request.args.get('task')
        if form.validate_on_submit():
            query = Tasks.query.filter_by(id=form.task_id.data).first()
            # take note that this is only for the first match where the value of
            # column_name = criteria and will not work with for statements. To get lla the cases where column_name = criteria
            # use .all() instead of .first() but you will need a for statement to get the invididual datebase rows
            query.duration = form.duration.data
            query.state = form.state.data
            # this updates the value of the column different_column_name

            db.session.add(query)
            db.session.commit()
            # flash sucsess message
            return redirect(url_for('homepage'))
            # return template editTask passing form and task
    else:
        flash('No task to edit')
        return redirect(url_for('homepage'))


@app.route('/debug')
def debugpage():
    raise RuntimeError('This is intentional')

if __name__ == '__main__':
    app.run()
