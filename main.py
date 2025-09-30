# main.py

import sys
import argparse
import pathlib
import yaml
from plywood_optimizer import create_cut_list
from output_generator import generate_html_output

def validate_data(project_data):
    # (This function is unchanged)
    required_keys = ['sheets', 'pieces', 'saw_kerf']
    if not all(key in project_data for key in required_keys):
        raise ValueError(f"YAML file is missing one or more required keys: {required_keys}")
    kerf = project_data['saw_kerf']
    if not isinstance(kerf, (int, float)) or kerf < 0:
        raise ValueError(f"'saw_kerf' must be a positive number, but got: {kerf}")
    sheet_dims_map = {}
    for i, sheet in enumerate(project_data['sheets']):
        if not all(key in sheet for key in ['type', 'width', 'height']):
            raise ValueError(f"Sheet #{i+1} in YAML is missing a required key ('type', 'width', or 'height').")
        if not all(isinstance(sheet[key], (int, float)) for key in ['width', 'height']) or not all(sheet[key] > 0 for key in ['width', 'height']):
            raise ValueError(f"Sheet '{sheet['type']}' must have positive numbers for width and height.")
        if 'cost' in sheet and (not isinstance(sheet['cost'], (int, float)) or sheet['cost'] < 0):
            raise ValueError(f"Sheet '{sheet['type']}' has an invalid 'cost'. It must be a positive number.")
        sheet_dims_map[sheet['type']] = {'width': sheet['width'], 'height': sheet['height']}
    for i, piece in enumerate(project_data['pieces']):
        if not all(key in piece for key in ['type', 'width', 'height']):
            raise ValueError(f"Piece #{i+1} in YAML is missing a required key ('type', 'width', or 'height').")
        if not all(isinstance(piece[key], (int, float)) for key in ['width', 'height']) or not all(piece[key] > 0 for key in ['width', 'height']):
            raise ValueError(f"Piece '{piece.get('name', f'#{i+1}')}' must have positive numbers for width and height.")
        if 'rotation' in piece and not isinstance(piece['rotation'], bool):
            raise ValueError(f"Piece '{piece.get('name', f'#{i+1}')}' has a non-boolean 'rotation' value. It must be true or false.")
        if piece['type'] not in sheet_dims_map:
            raise ValueError(f"Piece '{piece.get('name', f'#{i+1}')}' has type '{piece['type']}' which does not match any defined sheet type.")
        sheet_dims = sheet_dims_map[piece['type']]
        can_fit_unrotated = piece['width'] <= sheet_dims['width'] and piece['height'] <= sheet_dims['height']
        can_fit_rotated = piece.get('rotation', False) and (piece['height'] <= sheet_dims['width'] and piece['width'] <= sheet_dims['height'])
        if not (can_fit_unrotated or can_fit_rotated):
            raise ValueError(f"Piece '{piece.get('name', f'#{i+1}')}' ({piece['width']}w x {piece['height']}h) cannot fit on its sheet '{piece['type']}' in any allowed orientation.")
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
        
        validate_data(project_data)
        
        sheets = project_data['sheets']
        pieces_raw = project_data['pieces']
        kerf = project_data['saw_kerf']
        project_name = project_data.get('project_name', 'Untitled Project')
        
        expanded_pieces = []
        for piece_template in pieces_raw:
            quantity = piece_template.get('quantity', 1)
            for _ in range(quantity):
                expanded_pieces.append(piece_template.copy())

        print(f"✅ Project '{project_name}' loaded and validated. Optimizing...")

    except (ValueError, FileNotFoundError, yaml.YAMLError) as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    optimized_layout = create_cut_list(sheets, expanded_pieces, kerf)

    if optimized_layout:
        output_base_path = input_path.with_suffix('')
        print("\n✅ Optimization complete! Generating output files...")
        
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
            
            total_cost += num_sheets * sheet_info.get('cost', 0)

        yield_percentage = (total_piece_area / total_sheet_area * 100) if total_sheet_area > 0 else 0

        summary_details = {
            "kerf": kerf,
            "rotation_enabled": rotation_enabled,
            "yield_percentage": f"{yield_percentage:.3f}%", # <-- UPDATED
            "total_cost": total_cost
        }
        
        generate_html_output(optimized_layout, project_name, str(output_base_path), summary_details)
        
    else:
        print("❗️ Optimization resulted in an empty layout.")

if __name__ == "__main__":
    main()