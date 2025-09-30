# plywood_optimizer.py

import sys
from collections import defaultdict, Counter
import math

def _pack_sheet(sheet_dims, pieces_to_pack, kerf, scorer_func):
    # (This function is unchanged)
    sheet = {'width': sheet_dims['width'], 'height': sheet_dims['height'], 'pieces': []}
    free_rects = [{'x': 0, 'y': 0, 'width': sheet_dims['width'], 'height': sheet_dims['height']}]
    placed_piece_ids = set()
    while True:
        best_fit = {'score': float('inf'), 'piece': None, 'rect_index': -1, 'rotated': False}
        for piece in pieces_to_pack:
            if piece['id'] in placed_piece_ids: continue
            for j, rect in enumerate(free_rects):
                for is_rotated in [False, True]:
                    if is_rotated and not piece.get('rotation', False): continue
                    w, h = (piece['height'], piece['width']) if is_rotated else (piece['width'], piece['height'])
                    if w <= rect['width'] and h <= rect['height']:
                        score = scorer_func(w, h, rect)
                        if score < best_fit['score']:
                            best_fit.update({'score': score, 'piece': piece, 'rect_index': j, 'rotated': is_rotated})
        if best_fit['piece'] is None: break
        piece = best_fit['piece']
        rect = free_rects.pop(best_fit['rect_index'])
        placed_piece_ids.add(piece['id'])
        w, h = (piece['height'], piece['width']) if best_fit['rotated'] else (piece['width'], piece['height'])
        final_piece = piece.copy()
        final_piece.update({'width': w, 'height': h, 'x': rect['x'], 'y': rect['y']})
        sheet['pieces'].append(final_piece)
        if rect['height'] - h - kerf > 0:
            free_rects.append({'x': rect['x'], 'y': rect['y'] + h + kerf, 'width': rect['width'], 'height': rect['height'] - h - kerf})
        if rect['width'] - w - kerf > 0:
            free_rects.append({'x': rect['x'] + w + kerf, 'y': rect['y'], 'width': rect['width'] - w - kerf, 'height': h})
    unplaced_pieces = [p for p in pieces_to_pack if p['id'] not in placed_piece_ids]
    return sheet['pieces'], unplaced_pieces

def _solve_for_type(sheet_dims, pieces, kerf, scorer_func):
    # (This function is unchanged)
    all_sheets = []
    unplaced_pieces = list(pieces)
    while unplaced_pieces:
        sheet = { 'width': sheet_dims['width'], 'height': sheet_dims['height'], 'pieces': [], 'unplaced': [] }
        placed_on_sheet, unplaced_pieces = _pack_sheet(sheet_dims, unplaced_pieces, kerf, scorer_func)
        if placed_on_sheet:
            sheet['pieces'] = placed_on_sheet
            all_sheets.append(sheet)
        if not placed_on_sheet and unplaced_pieces:
            if all_sheets: all_sheets[-1]['unplaced'] = unplaced_pieces
            else: all_sheets.append({'pieces': [], 'unplaced': unplaced_pieces})
            break
    return all_sheets

def _generate_cut_sequence(parent_block, pieces):
    if len(pieces) <= 1:
        return []
    cuts = []
    y_coords = set()
    for p in pieces:
        y_coords.add(p['y'] + p['height'])
    for y_cut in sorted(list(y_coords)):
        if y_cut >= parent_block['y'] + parent_block['height']: continue
        top_pieces = [p for p in pieces if p['y'] >= y_cut]
        bottom_pieces = [p for p in pieces if p['y'] + p['height'] <= y_cut]
        if len(top_pieces) + len(bottom_pieces) == len(pieces):
            cuts.append(f"Rip cut at {y_cut:.3f}\" from the bottom edge.") # <-- UPDATED
            top_block = {'x': parent_block['x'], 'y': y_cut, 'width': parent_block['width'], 'height': parent_block['height'] - (y_cut - parent_block['y'])}
            bottom_block = {'x': parent_block['x'], 'y': parent_block['y'], 'width': parent_block['width'], 'height': y_cut - parent_block['y']}
            cuts.extend(_generate_cut_sequence(bottom_block, bottom_pieces))
            cuts.extend(_generate_cut_sequence(top_block, top_pieces))
            return cuts
    x_coords = set()
    for p in pieces:
        x_coords.add(p['x'] + p['width'])
    for x_cut in sorted(list(x_coords)):
        if x_cut >= parent_block['x'] + parent_block['width']: continue
        right_pieces = [p for p in pieces if p['x'] >= x_cut]
        left_pieces = [p for p in pieces if p['x'] + p['width'] <= x_cut]
        if len(right_pieces) + len(left_pieces) == len(pieces):
            cuts.append(f"Cross cut at {x_cut:.3f}\" from the left edge.") # <-- UPDATED
            right_block = {'x': x_cut, 'y': parent_block['y'], 'width': parent_block['width'] - (x_cut - parent_block['x']), 'height': parent_block['height']}
            left_block = {'x': parent_block['x'], 'y': parent_block['y'], 'width': x_cut - parent_block['x'], 'height': parent_block['height']}
            cuts.extend(_generate_cut_sequence(left_block, left_pieces))
            cuts.extend(_generate_cut_sequence(right_block, right_pieces))
            return cuts
    return cuts

def _run_strategy_contest(sheet_dims, pieces, saw_kerf, strategies):
    best_layout = None
    min_sheets = float('inf')
    best_strategy_name = "None"
    for strategy in strategies:
        sorted_pieces = sorted(pieces, key=strategy['sorter'], reverse=True)
        current_layout = _solve_for_type(sheet_dims, sorted_pieces, saw_kerf, strategy['scorer'])
        num_sheets = len(current_layout)
        unplaced_count = len(current_layout[-1].get('unplaced', [])) if current_layout else 0
        effective_sheets = num_sheets + unplaced_count * 100
        if effective_sheets < min_sheets:
            min_sheets = effective_sheets
            best_layout = current_layout
            best_strategy_name = strategy['name']
    
    print(f"  -> Best result found with strategy: '{best_strategy_name}' using {len(best_layout)} sheets.")
    total_piece_area = sum(p['width'] * p['height'] for p in pieces)
    total_sheet_area = len(best_layout) * (sheet_dims['width'] * sheet_dims['height'])
    if total_sheet_area > 0:
        waste_percentage = 100 * (1 - (total_piece_area / total_sheet_area))
        print(f"     Efficiency: {waste_percentage:.3f}% of material is waste.") # <-- UPDATED

    return best_layout

def create_cut_list(plywood_sheets, required_pieces, saw_kerf):
    # (This function is unchanged)
    STRATEGIES = [
        {'name': 'Sort by Area / Place by BAF', 'sorter': lambda p: p['width'] * p['height'], 'scorer': lambda w, h, r: (r['width'] * r['height']) - (w * h)},
        {'name': 'Sort by Area / Place by BSSF', 'sorter': lambda p: p['width'] * p['height'], 'scorer': lambda w, h, r: min(r['width'] - w, r['height'] - h)},
        {'name': 'Sort by Max Dimension / Place by BSSF', 'sorter': lambda p: max(p['width'], p['height']), 'scorer': lambda w, h, r: min(r['width'] - w, r['height'] - h)},
        {'name': 'Sort by Height / Place by BSSF', 'sorter': lambda p: p['height'], 'scorer': lambda w, h, r: min(r['width'] - w, r['height'] - h)},
        {'name': 'Sort by Width / Place by BSSF', 'sorter': lambda p: p['width'], 'scorer': lambda w, h, r: min(r['width'] - w, r['height'] - h)},
        {'name': 'Sort by Perimeter / Place by BAF', 'sorter': lambda p: 2*p['width'] + 2*p['height'], 'scorer': lambda w, h, r: (r['width'] * r['height']) - (w * h)},
        {'name': 'Sort by Area / Place by BLSF', 'sorter': lambda p: p['width'] * p['height'], 'scorer': lambda w, h, r: max(r['width'] - w, r['height'] - h)},
    ]
    pieces_by_type = defaultdict(list)
    for p in required_pieces:
        pieces_by_type[p['type']].append(p)
    sheets_by_type = {s['type']: {'width': s['width'], 'height': s['height']} for s in plywood_sheets}
    final_layout = {}
    for plywood_type, pieces in pieces_by_type.items():
        sheet_dims = sheets_by_type.get(plywood_type)
        if not sheet_dims: continue
        piece_fingerprints = [(p['width'], p['height'], p.get('rotation', False)) for p in pieces]
        counts = Counter(piece_fingerprints)
        if len(counts) > 0: divisor = math.gcd(*counts.values())
        else: divisor = 1
        if divisor > 1:
            print(f"\nDetected project consists of {divisor} identical kits for material '{plywood_type}'.")
            print("Optimizing for a single kit and multiplying the result...")
            single_kit = []
            for fingerprint, count in counts.items():
                for _ in range(count // divisor):
                    original_piece = next(p for p in pieces if (p['width'], p['height'], p.get('rotation', False)) == fingerprint)
                    single_kit.append(original_piece.copy())
            for i, p in enumerate(single_kit):
                p['id'] = p.get('name', 'Piece') + f"_kit1_{i+1}"
            kit_layout = _run_strategy_contest(sheet_dims, single_kit, saw_kerf, STRATEGIES)
            best_layout_for_type = kit_layout * divisor
        else:
            print(f"\nNo identical subsets found for '{plywood_type}'. Running full optimization...")
            for i, p in enumerate(pieces): p['id'] = p.get('name', 'Piece') + f"_{i+1}"
            best_layout_for_type = _run_strategy_contest(sheet_dims, pieces, saw_kerf, STRATEGIES)
        if best_layout_for_type:
            print("  -> Generating cut sequence for the best layout...")
            for sheet in best_layout_for_type:
                if sheet['pieces']:
                    initial_block = {'x': 0, 'y': 0, 'width': sheet_dims['width'], 'height': sheet_dims['height']}
                    sheet['cut_sequence'] = _generate_cut_sequence(initial_block, sheet['pieces'])
        final_layout[plywood_type] = best_layout_for_type
    return final_layout