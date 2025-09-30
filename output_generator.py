# output_generator.py

import json
from jinja2 import Environment, FileSystemLoader

def generate_html_output(layout, project_name, output_path_base, summary_details):
    """
    Renders the final HTML report. This version removes the SVG icons from the
    project summary and fixes the associated rendering bug.
    """
    
    summary_data = {m_type: len(sheets) for m_type, sheets in layout.items()}

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')

    # Prepare data for the template (the 'icons' dictionary is no longer needed)
    context = {
        "project_name": project_name,
        "layout": layout,
        "summary": summary_data,
        "details": summary_details
    }

    # Render the HTML
    html_content = template.render(context)
    
    # Save the generated HTML to a file
    html_filename = f"{output_path_base}_layout.html"
    try:
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Interactive HTML report saved to: {html_filename}")
    except Exception as e:
        print(f"❌ Error saving HTML file: {e}")