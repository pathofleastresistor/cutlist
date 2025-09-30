# Plywood Cut List Optimizer

This project is a Python-based tool that takes a list of required wooden parts and calculates an optimized layout to minimize waste on standard plywood sheets. It generates a modern, self-contained HTML report that provides a visual representation of the cut list and a detailed summary for workshop use.

The optimizer is built to be intelligent and robust, featuring:

* Multi-Strategy Optimization: The script runs a "contest" between several advanced packing algorithms (combinations of sorting heuristics and Guillotine packers like BSSF and BAF) and automatically picks the one that uses the fewest sheets.

* Grain Direction Control: You can specify whether a piece can be rotated 90 degrees, which is critical for maintaining grain direction in woodworking projects.

* Detailed HTML Reports: Generates a single, portable HTML file that is responsive, print-friendly, and includes interactive highlighting between the summary table and the visual layout.

* Robust Input Validation: The script validates your project file for common errors (impossible dimensions, missing keys, incorrect data types) before running, providing clear and helpful error messages.

## YAML Project File Format
To use the optimizer, you create a .yaml file that describes your project. The file has three required top-level keys: saw_kerf, sheets, and pieces.

Here is a template demonstrating all available fields:

YAML
```
# A descriptive name for your project (Optional).
project_name: "Workshop Cabinet"

# The width of your saw blade in inches (Required).
saw_kerf: 0.125

# A list of the stock material sheets you have available (Required).
sheets:
  - type: "3/4 inch Maple Plywood"
    width: 96
    height: 48
  - type: "1/2 inch MDF"
    width: 96
    height: 48

# The complete list of pieces you need to cut for the project (Required).
pieces:
  # This piece must maintain its grain direction.
  - name: "Cabinet Door" # (Optional) A descriptive name for the piece.
    type: "3/4 inch Maple Plywood" # (Required) Must match a type from the 'sheets' list.
    width: 18 # (Required)
    height: 24 # (Required)
    # 'rotation' is omitted, so it defaults to false.

  # These pieces can be batched together.
  - name: "Shelf"
    type: "3/4 inch Maple Plywood"
    width: 22.5
    height: 12
    quantity: 4 # (Optional) Defaults to 1 if omitted.

  # The grain direction for this piece does not matter.
  - name: "Internal Brace"
    type: "3/4 inch Maple Plywood"
    width: 10
    height: 4
    quantity: 8
    rotation: true # (Optional) Allows the optimizer to rotate this piece 90 degrees. Defaults to false.
```

## How to Use
Follow these steps to set up and run the optimizer.

### Install dependencies
```
pip install -r requirements.txt
```

### Create a Project File
Create a new file with a .yaml extension (e.g., my_project.yaml). Use the template above to define your plywood sheets and the pieces you need to cut.

### Run the Script
Open your terminal or command prompt, navigate to the project folder, and run the main.py script, passing your project file as an argument:

```
python main.py my_project.yaml
```

You will see progress in the console as the optimizer tests various strategies to find the best layout.

### View the Output
After the script finishes, it will generate a new HTML report file in the same folder (e.g., my_project_layout.html).

Open this file in any modern web browser to view the interactive and printable cut list report.

## Project File Structure
* main.py: The main entry point you run from the command line. It handles file I/O and orchestrates the process.

* plywood_optimizer.py: The core optimization engine. It contains the packing algorithms and the multi-strategy "contest" logic.

* output_generator.py: Responsible for creating the final, self-contained HTML report file.

* *.yaml: Your project definition files.