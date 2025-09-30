# main.py

import sys
import argparse
import pathlib
import yaml
from plywood_optimizer import create_cut_list
from output_generator import generate_html_output

def validate_data(project_data):
    """Performs rigorous checks on the project data from the YAML file."""
    # ... (previous validation logic is the same) ...
    
    sheet_dims_map = {}
    for i, sheet in enumerate(project_data['sheets']):
        # ... (other sheet validation logic) ...
        
        # **NEW: Validate the optional 'cost' key**
        if 'cost' in sheet and (not isinstance(sheet['cost'], (int, float)) or sheet['cost'] < 0):
            raise ValueError(f"Sheet '{sheet['type']}' has an invalid 'cost'. It must be a positive number.")

        sheet_dims_map[sheet['type']] = {'width': sheet['width'], 'height': sheet['height']}

    # ... (rest of the validation logic is the same) ...
    return True

def main():
    parser = argparse.ArgumentParser(description="Plywood Cut List Optimizer")
    parser.add_argument('project_file', type=str, help="Path to the project's .yaml file")
    args = parser.parse_args()
    
    try:
        input_path = pathlib.Path(args.project_file)
        with open(input_path, 'r') as f:
            project_data = yaml.safe_load(f)
        if project_data is None: raise ValueError("File is empty or invalid.")
        
        # The full validate_data function should be here
        # validate_data(project_data) 
        
        sheets = project_data['sheets']
        pieces_raw = project_data['pieces']
        kerf = project_data['saw_kerf']
        project_name = project_data.get('project_name', 'Untitled Project')
        
        expanded_pieces = []
        for piece_template in pieces_raw:
            quantity = piece_template.get('quantity', 1)
            for _ in range(quantity):
                expanded_pieces.append(piece_template.copy())

        print(f"✅ Project '{project_name}' loaded. Optimizing...")

    except (ValueError, FileNotFoundError, yaml.YAMLError) as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    optimized_layout = create_cut_list(sheets, expanded_pieces, kerf)

    if optimized_layout:
        output_base_path = input_path.with_suffix('')
        print("\n✅ Optimization complete! Generating output files...")
        
        # --- Gather final summary details ---
        rotation_enabled = any(p.get('rotation', False) for p in expanded_pieces)
        sheets_by_type = {s['type']: s for s in sheets}
        
        total_piece_area = 0
        total_sheet_area = 0
        total_cost = 0

        for type, layout_sheets in optimized_layout.items():
            pieces_of_type = [p for p in expanded_pieces if p['type'] == type]
            total_piece_area += sum(p['width'] * p['height'] for p in pieces_of_type)
            
            sheet_info = sheets_by_type[type]
            num_sheets = len(layout_sheets)
            total_sheet_area += num_sheets * (sheet_info['width'] * sheet_info['height'])
            
            # **NEW: Calculate total cost**
            total_cost += num_sheets * sheet_info.get('cost', 0)

        yield_percentage = (total_piece_area / total_sheet_area * 100) if total_sheet_area > 0 else 0

        summary_details = {
            "kerf": kerf,
            "rotation_enabled": rotation_enabled,
            "yield_percentage": f"{yield_percentage:.2f}%",
            "total_cost": total_cost # Add cost to the details
        }
        
        generate_html_output(optimized_layout, project_name, str(output_base_path), summary_details)
        
    else:
        print("❗️ Optimization resulted in an empty layout.")

if __name__ == "__main__":
    main()