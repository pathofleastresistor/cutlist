from flask import Flask, render_template, request, redirect, url_for, flash
import json
from optimizer import create_cut_list
from database import init_db, save_project, get_all_projects, get_project, delete_project, update_project

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-for-flashing-messages'
init_db(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            form_data = request.form
            project_name = form_data.get('project_name', 'Untitled Project')
            saw_kerf = float(form_data['saw_kerf'])
            
            sheets = []
            for i in range(len(form_data.getlist('sheet_type[]'))):
                sheets.append({
                    'type': form_data.getlist('sheet_type[]')[i],
                    'width': float(form_data.getlist('sheet_width[]')[i]),
                    'height': float(form_data.getlist('sheet_height[]')[i]),
                    'cost': float(form_data.getlist('sheet_cost[]')[i] or 0)
                })

            pieces = []
            checked_rotations = request.form.getlist('piece_rotation[]')
            for i in range(len(form_data.getlist('piece_name[]'))):
                pieces.append({
                    'name': form_data.getlist('piece_name[]')[i] or f'Piece {i+1}',
                    'type': form_data.getlist('piece_type[]')[i],
                    'width': float(form_data.getlist('piece_width[]')[i]),
                    'height': float(form_data.getlist('piece_height[]')[i]),
                    'quantity': int(form_data.getlist('piece_quantity[]')[i] or 1),
                    'rotation': str(i) in checked_rotations
                })

            input_data = {
                'project_name': project_name,
                'saw_kerf': saw_kerf,
                'sheets': sheets,
                'pieces': pieces
            }
            
            expanded_pieces = []
            for p in pieces:
                for _ in range(p.get('quantity', 1)):
                    expanded_pieces.append(p.copy())

            results = create_cut_list(sheets, expanded_pieces, saw_kerf)
            
            project_id = request.form.get('project_id')
            project_obj = get_project(project_id) if project_id else None
            
            # THIS IS THE FIX: Create a simple dictionary to pass to the template
            project_data_for_template = None
            if project_obj:
                project_data_for_template = {"id": project_obj.id, "name": project_obj.name}

            return render_template('index.html', inputs=input_data, results=results, project=project_data_for_template)

        except Exception as e:
            flash(f"An error occurred: {e}", 'error')
            return render_template('index.html', inputs=request.form, results=None, project=None)

    return render_template('index.html', inputs=None, results=None, project=None)

@app.route('/view_project/<int:project_id>')
def view_project(project_id):
    project_obj = get_project(project_id)
    if project_obj:
        inputs = json.loads(project_obj.input_data)
        results=json.loads(project_obj.result_data)
        
        # THIS IS THE FIX: Create a simple dictionary instead of passing the whole object
        project_data_for_template = {
            "id": project_obj.id,
            "name": project_obj.name
        }
        
        return render_template('index.html', inputs=inputs, results=results, project=project_data_for_template)
    
    flash('Project not found.', 'error')
    return redirect(url_for('projects'))

@app.route('/save_project', methods=['POST'])
def save_project_route():
    try:
        project_id = request.form.get('project_id')
        project_name = request.form['project_name']
        input_data_json = request.form['input_data']
        result_data_json = request.form['result_data']
        
        inputs = json.loads(input_data_json)
        results = json.loads(result_data_json)

        if project_id:
            update_project(project_id, project_name, inputs, results)
            flash('Project updated successfully!', 'success')
        else:
            save_project(project_name, inputs, results)
            flash('Project saved successfully!', 'success')
    except Exception as e:
        flash(f'Error saving/updating project: {e}', 'error')
        
    return redirect(url_for('projects'))

@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project_route(project_id):
    try:
        delete_project(project_id)
        flash('Project deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting project: {e}', 'error')
    return redirect(url_for('projects'))

@app.route('/projects')
def projects():
    all_projects = get_all_projects()
    return render_template('projects.html', projects=all_projects)

if __name__ == '__main__':
    app.run(debug=True)

