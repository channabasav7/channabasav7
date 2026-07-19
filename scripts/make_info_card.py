import os
import sys

def generate_info_card(svg_path):
    # Terminal properties
    width = 490
    height = 570
    
    # Check if STATIC mode is enabled
    is_static = os.environ.get("STATIC") == "1"
    
    lines = [
        ("prompt", "channabasav7@github ~ $ ./neofetch.sh"),
        ("separator", "--------------------------------------"),
        ("info", "OS", "GitHub Profile README"),
        ("info", "Host", "github.com/channabasav7"),
        ("info", "Kernel", "SVG / Python 3.11 / GH Actions"),
        ("info", "Uptime", "Live since 2023"),
        ("info", "Shell", "powershell / bash"),
        ("separator2", ""),
        ("info", "Role", "Fullstack & Mobile Developer"),
        ("info", "Stack", "Flutter, Dart, Python, React, Node.js"),
        ("info", "Projects", "Viora (Flutter), Land Registration"),
        ("info", "Highlights", "Mobile Developer, Web3 Tech Enthusiast"),
        ("separator3", ""),
        ("colors_header", "System Colors:"),
        ("colors", "")
    ]
    
    svg_content = []
    svg_content.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    
    # Styles
    svg_content.append('  <style>')
    svg_content.append('    :root {')
    svg_content.append('      --bg: #0d1117;')
    svg_content.append('      --border: #30363d;')
    svg_content.append('      --title-bar: #161b22;')
    svg_content.append('      --title-text: #8b949e;')
    svg_content.append('      --text: #c9d1d9;')
    svg_content.append('      --prompt: #58a6ff;')
    svg_content.append('      --label: #7ee787;')
    svg_content.append('    }')
    svg_content.append('    @media (prefers-color-scheme: light) {')
    svg_content.append('      :root {')
    svg_content.append('        --bg: #ffffff;')
    svg_content.append('        --border: #d0d7de;')
    svg_content.append('        --title-bar: #f6f8fa;')
    svg_content.append('        --title-text: #57606a;')
    svg_content.append('        --text: #24292f;')
    svg_content.append('        --prompt: #0969da;')
    svg_content.append('        --label: #1a7f37;')
    svg_content.append('      }')
    svg_content.append('    }')
    svg_content.append('    .terminal {')
    svg_content.append('      fill: var(--bg);')
    svg_content.append('      stroke: var(--border);')
    svg_content.append('      stroke-width: 1.5;')
    svg_content.append('    }')
    svg_content.append('    .title-bar {')
    svg_content.append('      fill: var(--title-bar);')
    svg_content.append('      stroke: var(--border);')
    svg_content.append('      stroke-width: 1.5;')
    svg_content.append('    }')
    svg_content.append('    .title-text {')
    svg_content.append('      font-family: ui-monospace, SFMono-Regular, SF Mono, Consolas, monospace;')
    svg_content.append('      font-size: 13px;')
    svg_content.append('      font-weight: 600;')
    svg_content.append('      fill: var(--title-text);')
    svg_content.append('    }')
    svg_content.append('    text.terminal-text {')
    svg_content.append('      font-family: ui-monospace, SFMono-Regular, SF Mono, Consolas, monospace;')
    svg_content.append('      font-size: 12px;')
    svg_content.append('      fill: var(--text);')
    svg_content.append('    }')
    svg_content.append('    .prompt-text { fill: var(--prompt); font-weight: bold; }')
    svg_content.append('    .label-text { fill: var(--label); font-weight: bold; }')
    
    if not is_static:
        svg_content.append('    @keyframes fadeInSlide {')
        svg_content.append('      0% { opacity: 0; transform: translateY(8px); }')
        svg_content.append('      100% { opacity: 1; transform: translateY(0); }')
        svg_content.append('    }')
        svg_content.append('    .line {')
        svg_content.append('      opacity: 0;')
        svg_content.append('      animation: fadeInSlide 0.4s ease-out forwards;')
        svg_content.append('    }')
        # Generate line delays
        for idx in range(len(lines)):
            delay = 0.1 + idx * 0.05
            svg_content.append(f'    .line-{idx} {{ animation-delay: {delay:.2f}s; }}')
            
    svg_content.append('  </style>')
    
    # Drop shadow filter
    svg_content.append('  <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">')
    svg_content.append('    <feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity="0.15" />')
    svg_content.append('  </filter>')
    
    # Terminal Window (Background & Border)
    svg_content.append(f'  <rect class="terminal" x="10" y="10" width="{width-20}" height="{height-20}" rx="8" ry="8" filter="url(#shadow)" />')
    
    # Title Bar
    svg_content.append(f'  <path class="title-bar" d="M 10,18 A 8,8 0 0,1 18,10 L {width-18},10 A 8,8 0 0,1 {width-10},18 L {width-10},42 L 10,42 Z" />')
    
    # Window Control Buttons
    svg_content.append('  <circle cx="28" cy="26" r="6" fill="#ff5f56" />')
    svg_content.append('  <circle cx="48" cy="26" r="6" fill="#ffbd2e" />')
    svg_content.append('  <circle cx="68" cy="26" r="6" fill="#27c93f" />')
    
    # Title Text
    svg_content.append(f'  <text class="title-text" x="{width/2}" y="31" text-anchor="middle">channabasav7@terminal</text>')
    
    # Content Area
    start_y = 75
    y_gap = 26
    
    for idx, item in enumerate(lines):
        line_type = item[0]
        y_pos = start_y + idx * y_gap
        
        # Build line elements
        class_str = f' class="line line-{idx}"' if not is_static else ''
        svg_content.append(f'  <g{class_str}>')
        
        if line_type == "prompt":
            svg_content.append(f'    <text class="terminal-text" x="35" y="{y_pos}"><tspan class="prompt-text">channabasav7@github</tspan> <tspan class="prompt-text">~</tspan> <tspan class="prompt-text">$</tspan> neofetch</text>')
        elif line_type in ["separator", "separator2", "separator3"]:
            svg_content.append(f'    <text class="terminal-text" x="35" y="{y_pos}" opacity="0.3">{item[1]}</text>')
        elif line_type == "info":
            label, val = item[1], item[2]
            svg_content.append(f'    <text class="terminal-text" x="35" y="{y_pos}"><tspan class="label-text">{label}:</tspan> {val}</text>')
        elif line_type == "colors_header":
            svg_content.append(f'    <text class="terminal-text" x="35" y="{y_pos}" style="fill: var(--title-text); font-weight: bold;">{item[1]}</text>')
        elif line_type == "colors":
            # Draw color block rectangles
            colors_list = ["#1f2328", "#ff5f56", "#27c93f", "#ffbd2e", "#58a6ff", "#bc8cff", "#39d353", "#c9d1d9"]
            for c_idx, c_code in enumerate(colors_list):
                block_x = 35 + c_idx * 24
                svg_content.append(f'    <rect x="{block_x}" y="{y_pos - 10}" width="18" height="14" fill="{c_code}" rx="2" />')
                
        svg_content.append('  </g>')
        
    svg_content.append('</svg>')
    
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(svg_content))
    print(f"Successfully generated info-card SVG at '{svg_path}'")

if __name__ == "__main__":
    svg_out = "info-card.svg"
    if len(sys.argv) > 1:
        svg_out = sys.argv[1]
    generate_info_card(svg_out)
