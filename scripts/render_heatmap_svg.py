import os
import sys
import json
from datetime import datetime, timedelta

def render_heatmap(json_path, svg_path):
    if not os.path.exists(json_path):
        print(f"Error: JSON file '{json_path}' not found. Run fetch_contributions.py first.")
        sys.exit(1)
        
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    days = data.get("days", [])
    if not days:
        print("Error: No day data found in contributions.json.")
        sys.exit(1)
        
    # Check for STATIC mode
    is_static = os.environ.get("STATIC") == "1"
    
    # Calculate coordinate layout
    # First day's date
    start_date = datetime.strptime(days[0]["date"], "%Y-%m-%d")
    
    def get_wday(dt):
        # 0 = Sunday, 6 = Saturday
        return (dt.weekday() + 1) % 7
        
    first_sunday = start_date - timedelta(days=get_wday(start_date))
    
    # Determine columns and rows
    # Grid: 53 columns, 7 rows
    grid_cells = []
    col_months = {}
    
    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        days_diff = (dt - first_sunday).days
        col_idx = days_diff // 7
        row_idx = days_diff % 7
        
        # We only render within a standard 53-week view (cols 0-52)
        if 0 <= col_idx < 53:
            grid_cells.append({
                "col": col_idx,
                "row": row_idx,
                "count": d["count"],
                "level": d["level"],
                "date": d["date"]
            })
            
            if col_idx not in col_months:
                col_months[col_idx] = []
            col_months[col_idx].append(dt)
            
    # Extract month labels
    month_labels = []
    last_month = None
    for col in sorted(col_months.keys()):
        dts = col_months[col]
        # Month name of the first day of that week
        m_name = dts[0].strftime("%b")
        if m_name != last_month:
            month_labels.append((col, m_name))
            last_month = m_name
            
    # Filter month labels to avoid overlaps (must be at least 3 weeks apart)
    filtered_month_labels = []
    last_col = -10
    for col, m_name in month_labels:
        if col - last_col >= 3:
            filtered_month_labels.append((col, m_name))
            last_col = col
            
    # Layout spacing constants
    box_size = 10
    gap = 3
    x_start = 85
    y_start = 35
    
    svg_width = 860
    svg_height = 180
    
    svg_content = []
    svg_content.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">')
    svg_content.append('  <style>')
    svg_content.append('    :root {')
    svg_content.append('      --bg: #ffffff;')
    svg_content.append('      --border: #d0d7de;')
    svg_content.append('      --text: #57606a;')
    svg_content.append('      --color-0: #ebedf0;')
    svg_content.append('      --color-1: #9be9a8;')
    svg_content.append('      --color-2: #40c463;')
    svg_content.append('      --color-3: #30a14e;')
    svg_content.append('      --color-4: #216e39;')
    svg_content.append('      --color-5: #154f24;')
    svg_content.append('    }')
    svg_content.append('    @media (prefers-color-scheme: dark) {')
    svg_content.append('      :root {')
    svg_content.append('        --bg: #0d1117;')
    svg_content.append('        --border: #30363d;')
    svg_content.append('        --text: #8b949e;')
    svg_content.append('        --color-0: #161b22;')
    svg_content.append('        --color-1: #0e4429;')
    svg_content.append('        --color-2: #006d32;')
    svg_content.append('        --color-3: #26a641;')
    svg_content.append('        --color-4: #39d353;')
    svg_content.append('        --color-5: #69f0a0;')
    svg_content.append('      }')
    svg_content.append('    }')
    svg_content.append('    .background {')
    svg_content.append('      fill: var(--bg);')
    svg_content.append('      stroke: var(--border);')
    svg_content.append('      stroke-width: 1.5;')
    svg_content.append('    }')
    svg_content.append('    .label {')
    svg_content.append('      font-family: ui-monospace, SFMono-Regular, SF Mono, Consolas, monospace;')
    svg_content.append('      font-size: 10px;')
    svg_content.append('      fill: var(--text);')
    svg_content.append('    }')
    svg_content.append('    .contrib-box {')
    svg_content.append('      rx: 2px;')
    svg_content.append('      ry: 2px;')
    svg_content.append('    }')
    
    if not is_static:
        svg_content.append('    @keyframes slideIn {')
        svg_content.append('      0% { opacity: 0; transform: translateY(-6px); }')
        svg_content.append('      100% { opacity: 1; transform: translateY(0); }')
        svg_content.append('    }')
        svg_content.append('    .contrib-box {')
        svg_content.append('      opacity: 0;')
        svg_content.append('      animation: slideIn 0.3s ease-out forwards;')
        svg_content.append('    }')
        
    svg_content.append('  </style>')
    
    # Shadow and background card
    svg_content.append('  <filter id="card-shadow" x="-5%" y="-5%" width="110%" height="110%">')
    svg_content.append('    <feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity="0.1" />')
    svg_content.append('  </filter>')
    svg_content.append(f'  <rect class="background" x="10" y="10" width="{svg_width - 20}" height="{svg_height - 20}" rx="8" ry="8" filter="url(#shadow)" />')
    
    # Render Month Labels
    for col, m_name in filtered_month_labels:
        x = x_start + col * (box_size + gap)
        svg_content.append(f'  <text class="label" x="{x}" y="25">{m_name}</text>')
        
    # Render Day Labels (Mon, Wed, Fri)
    svg_content.append(f'  <text class="label" x="45" y="{y_start + 1 * (box_size + gap) + 9}">Mon</text>')
    svg_content.append(f'  <text class="label" x="45" y="{y_start + 3 * (box_size + gap) + 9}">Wed</text>')
    svg_content.append(f'  <text class="label" x="45" y="{y_start + 5 * (box_size + gap) + 9}">Fri</text>')
    
    # Render Grid Cells
    for cell in grid_cells:
        col = cell["col"]
        row = cell["row"]
        level = cell["level"]
        count = cell["count"]
        date = cell["date"]
        
        x = x_start + col * (box_size + gap)
        y = y_start + row * (box_size + gap)
        
        # Assign neon color level 5 for best day(s) or very high counts
        fill_level = level
        if level == 4 and count > 15:
            fill_level = 5
            
        color_fill = f"var(--color-{fill_level})"
        
        # Tooltip text
        title_text = f"{count} contributions on {date}"
        
        if is_static:
            svg_content.append(f'  <rect class="contrib-box" x="{x}" y="{y}" width="{box_size}" height="{box_size}" fill="{color_fill}"><title>{title_text}</title></rect>')
        else:
            delay = (col + row) * 0.015
            svg_content.append(f'  <rect class="contrib-box" x="{x}" y="{y}" width="{box_size}" height="{box_size}" fill="{color_fill}" style="animation-delay: {delay:.3f}s;"><title>{title_text}</title></rect>')
            
    # Render Footer Stats
    total = data.get("total_contributions", 0)
    streak = data.get("current_streak", 0)
    longest = data.get("longest_streak", 0)
    footer_text = f"{total:,} contributions in the last year | Streak: {streak} days (longest: {longest} days)"
    svg_content.append(f'  <text class="label" x="{x_start}" y="152" style="font-weight: 600;">{footer_text}</text>')
    
    # Render Legend
    legend_start = svg_width - 240
    svg_content.append(f'  <text class="label" x="{legend_start}" y="152">Less</text>')
    for i in range(6):
        leg_x = legend_start + 32 + i * (box_size + gap)
        color_fill = f"var(--color-{i})"
        svg_content.append(f'  <rect class="contrib-box" x="{leg_x}" y="142" width="{box_size}" height="{box_size}" fill="{color_fill}" />')
    svg_content.append(f'  <text class="label" x="{legend_start + 32 + 6 * (box_size + gap) + 5}" y="152">More</text>')
    
    svg_content.append('</svg>')
    
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(svg_content))
    print(f"Successfully generated heatmap SVG at '{svg_path}'")

if __name__ == "__main__":
    json_in = "data/contributions.json"
    svg_out = "contrib-heatmap.svg"
    
    if len(sys.argv) > 1:
        json_in = sys.argv[1]
    if len(sys.argv) > 2:
        svg_out = sys.argv[2]
        
    render_heatmap(json_in, svg_out)
