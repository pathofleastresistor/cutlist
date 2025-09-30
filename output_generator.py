# output_generator.py

import json

def generate_html_output(layout, project_name, output_path_base, summary_details):
    """
    Generates a single, self-contained HTML file with a modern, responsive layout
    using Tailwind CSS and AlpineJS, optimized for printing. This is the complete
    and final version incorporating all features and bug fixes.
    """
    
    # Pre-process data for the material summary
    summary_data = {m_type: len(sheets) for m_type, sheets in layout.items()}

    # --- SVG Icons ---
    icons = {
        "material": '<svg class="w-5 h-5 mr-3 text-sky-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>',
    }

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cut List: {project_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <style>
        @media print {{
            body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            .no-print {{ display: none !important; }}
            .print-card {{ box-shadow: none !important; border: 1px solid #ccc !important; }}
            @page {{ margin: 0.5in; }}
        }}
    </style>
</head>
<body class="bg-slate-100 font-sans" x-data="cutlistReport()">
    <header class="bg-slate-800 text-white p-6 text-center no-print">
        <h1 class="text-4xl font-bold">{project_name}</h1>
    </header>

    <main class="p-4 md:p-8 max-w-7xl mx-auto">
        <div class="bg-white p-6 rounded-xl shadow-md mb-8 print-card">
            <h2 class="text-2xl font-bold text-slate-700 border-b pb-2 mb-4">Project Summary</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8">
                <ul class="space-y-2">
                    <template x-for="([type, count]) in Object.entries(summary)">
                        <li class="flex items-center text-slate-600">{icons['material']}<span><strong x-text="count + ' sheet(s)'"></strong> of <strong x-text="type"></strong></span></li>
                    </template>
                </ul>
                <ul class="space-y-2 mt-4 md:mt-0 pt-4 md:pt-0 border-t md:border-t-0 md:border-l md:pl-8 border-slate-200">
                    <li class="flex items-center text-slate-600"><span>Saw Kerf: <strong x-text="details.kerf + '&quot;'"></strong></span></li>
                    <li class="flex items-center text-slate-600"><span>Rotation: <strong x-text="details.rotation_enabled ? 'Enabled' : 'Disabled'"></strong></span></li>
                    <li class="flex items-center text-slate-600"><span>Material Yield: <strong x-text="details.yield_percentage"></strong></span></li>
                </ul>
            </div>
        </div>

        <template x-for="([type, sheets]) in Object.entries(layout)">
            <div>
                <h2 class="text-3xl font-bold text-slate-800 mb-6" x-text="'Material: ' + type"></h2>
                <template x-for="(sheet, index) in sheets">
                    <div class="bg-white rounded-xl shadow-lg mb-8 overflow-hidden print-card">
                        <div class="p-6">
                            <h3 class="text-xl font-bold text-slate-600 mb-4" x-text="'Sheet ' + (index + 1) + ' of ' + sheets.length"></h3>
                            
                            <div class="relative w-full bg-slate-200 border border-slate-300 mb-6" 
                                 :style="`aspect-ratio: ${{sheet.width}} / ${{sheet.height}}`">
                                <template x-for="piece in sheet.pieces">
                                    <div class="absolute box-border flex items-center justify-center overflow-hidden transition-all duration-150"
                                        :style="`
                                            left: ${{ (piece.x / sheet.width * 100) }}%;
                                            bottom: ${{ (piece.y / sheet.height * 100) }}%;
                                            width: ${{ (piece.width / sheet.width * 100) }}%;
                                            height: ${{ (piece.height / sheet.height * 100) }}%;
                                            background-color: ${{pieceColor(piece.id)}};
                                            border: 1px solid rgba(0,0,0,0.3);
                                        `"
                                        :class="{{ 'ring-4 ring-offset-2 ring-sky-500 z-10': highlightedPiece === piece.id }}">
                                        <div class="text-[8px] md:text-[10px] font-bold text-center p-1 break-words"
                                             :style="`color: getContrastColor(pieceColor(piece.id))`"
                                             x-text="piece.id + ' (' + piece.width + '&quot;x' + piece.height + '&quot;)'"></div>
                                    </div>
                                </template>
                            </div>

                            <div class="overflow-x-auto">
                                <table class="w-full text-sm text-left text-slate-500">
                                    <thead class="text-xs text-slate-700 uppercase bg-slate-50">
                                        <tr><th class="px-4 py-3">Piece</th><th class="px-4 py-3">Dimensions</th><th class="px-4 py-3">Position</th></tr>
                                    </thead>
                                    <tbody>
                                        <template x-for="piece in sheet.pieces">
                                            <tr class="border-b hover:bg-slate-50" @mouseenter="highlightedPiece = piece.id" @mouseleave="highlightedPiece = null">
                                                <td class="px-4 py-2 font-medium text-slate-900" x-text="piece.id"></td>
                                                <td class="px-4 py-2" x-text="piece.width + '&quot; x ' + piece.height + '&quot;'"></td>
                                                <td class="px-4 py-2" x-text="piece.x.toFixed(2) + ', ' + piece.y.toFixed(2)"></td>
                                            </tr>
                                        </template>
                                        <template x-if="sheet.unplaced && sheet.unplaced.length > 0">
                                            <tr><td colspan="3" class="px-4 py-2 text-orange-600 font-semibold bg-orange-50">Unplaced Pieces:</td></tr>
                                            <template x-for="unplacedPiece in sheet.unplaced">
                                                <tr class="border-b bg-orange-50"><td class="px-4 py-2" x-text="unplacedPiece.id"></td><td class="px-4 py-2" x-text="unplacedPiece.width + '&quot; x ' + unplacedPiece.height + '&quot;'"></td><td class="px-4 py-2 text-xs">N/A</td></tr>
                                            </template>
                                        </template>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </template>
            </div>
        </template>
    </main>
    
    <script>
        function cutlistReport() {{
            const layoutData = {json.dumps(layout)};
            const summaryData = {json.dumps(summary_data)};
            const detailsData = {json.dumps(summary_details)};

            // Pre-sort the pieces in each sheet by ID to ensure consistency between table and visual.
            for (const type in layoutData) {{
                if (layoutData.hasOwnProperty(type)) {{
                    layoutData[type].forEach(sheet => {{
                        if (sheet.pieces) {{
                            sheet.pieces.sort((a, b) => a.id.localeCompare(b.id));
                        }}
                    }});
                }}
            }}

            return {{
                layout: layoutData,
                summary: summaryData,
                details: detailsData,
                highlightedPiece: null,
                _pieceColors: {{}},
                _colorPalette: ['#a1b4cc', '#c0d6e6', '#e0b3b3', '#d4c7b8', '#b3cbe0', '#e0d8b3', '#a1e0c7', '#c7a1e0', '#b3a1cc', '#c7e0a1', '#e0c7a1', '#a1cce0', '#d8e0a1', '#e0a1c7', '#a1d8e0', '#d8a1e0'],
                _colorIndex: 0,
                pieceColor(id) {{
                    if (!this._pieceColors[id]) {{
                        this._pieceColors[id] = this._colorPalette[this._colorIndex++ % this._colorPalette.length];
                    }}
                    return this._pieceColors[id];
                }},
                getContrastColor(hexcolor) {{
                    if (!hexcolor || hexcolor.length < 7) return 'white';
                    const r = parseInt(hexcolor.substring(1, 3), 16);
                    const g = parseInt(hexcolor.substring(3, 5), 16);
                    const b = parseInt(hexcolor.substring(5, 7), 16);
                    const luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;
                    return luminance > 0.5 ? '#212529' : 'white';
                }}
            }}
        }}
    </script>
</body>
</html>
    """
    html_filename = f"{output_path_base}_layout.html"
    try:
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_template)
        print(f"✅ Modern HTML report saved to: {html_filename}")
    except IOError as e:
        print(f"❌ Error saving HTML file: {e}")