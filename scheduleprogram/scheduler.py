# all the imports
from flask import Flask, render_template

# configuration
from flask.ext.sqlalchemy import SQLAlchemy

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


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    project = db.Column(db.String(80), unique=True)

    # modules = db.relationship("Modules" , backref ='project')

    def __init__(self, username, project):
        self.username = username
        self.project = project

    def __repr__(self):
        return '<Project %r>' % self.project


class Modules(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modulename = db.Column(db.String(80), unique=True)
    project = db.Column(db.String(80))
    # tasks = db.relationship("Tasks")
    # project_id = db.Column(db.Integer, db.ForeignKey('Project.id'))


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    taskname = db.Column(db.String(120))
    module = db.Column(db.String(80))
    # modules_id = db.Column(db.Integer, db.ForeignKey('Modules.id'))


@app.route('/initdb')
def page():
    db.create_all()
    project = Project('testuser', 'test project')
    db.session.add(project)
    db.session.commit()
    query = Project.query.order_by(Project.username)
    return render_template('test.html', output=query)


@app.route('/')
def page2():
    query = Project.query.order_by(Project.username)
    return render_template('test.html', output=query)


if __name__ == '__main__':
    app.run()
