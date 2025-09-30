from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime

db = SQLAlchemy()

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    input_data = db.Column(db.Text, nullable=False) # Stored as JSON
    result_data = db.Column(db.Text, nullable=False) # Stored as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Project {self.name}>'

def init_db(app):
    """Initializes the database and creates tables if they don't exist."""
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()

def save_project(name, inputs, results):
    """Saves a new project to the database."""
    project = Project(
        name=name,
        input_data=json.dumps(inputs),
        result_data=json.dumps(results)
    )
    db.session.add(project)
    db.session.commit()

def update_project(project_id, name, inputs, results):
    """Updates an existing project in the database."""
    project = Project.query.get(project_id)
    if project:
        project.name = name
        project.input_data = json.dumps(inputs)
        project.result_data = json.dumps(results)
        db.session.commit()

def get_all_projects():
    """Retrieves all saved projects, newest first."""
    return Project.query.order_by(Project.created_at.desc()).all()

def get_project(project_id):
    """Retrieves a single project by its ID."""
    return Project.query.get(project_id)

def delete_project(project_id):
    """Deletes a project from the database by its ID."""
    project = Project.query.get(project_id)
    if project:
        db.session.delete(project)
        db.session.commit()

