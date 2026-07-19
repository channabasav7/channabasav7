import os
import sys
from PIL import Image

def generate_ascii_svg(image_path, svg_path):
    if not os.path.exists(image_path):
        print(f"Error: Prepped image '{image_path}' not found.")
        sys.exit(1)
        
    img = Image.open(image_path).convert("L")
    w, h = img.size
    
    # Grid dimensions (target cols = 85, rows calculated based on aspect ratio)
    cols = 85
    char_aspect_ratio = 0.6  # Monospace width/height ratio
    rows = int(cols * (h / w) * char_aspect_ratio)
    rows = max(10, min(100, rows)) # clamping
    
    print(f"Resizing image to grid: {cols} columns x {rows} rows")
    img_resized = img.resize((cols, rows), Image.Resampling.LANCZOS)
    
    # Ramp of characters from bright (sparse) to dark (dense)
    RAMP = " .`:-=+*cs#%@"
    ramp_len = len(RAMP)
    
    # Convert pixels to characters
    ascii_rows = []
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            pixel = img_resized.getpixel((c, r))
            # 255 -> index 0 (space)
            # 0   -> index ramp_len - 1 (@)
            idx = int((255 - pixel) / 255.0 * (ramp_len - 1))
            row_chars.append(RAMP[idx])
        ascii_rows.append("".join(row_chars))
        
    # SVG Setup
    char_width = 6.0
    char_height = 11.0
    svg_width = cols * char_width
    svg_height = rows * char_height + 10.0
    
    # Animation settings
    row_duration = 0.2     # duration for typing one row (seconds)
    row_stagger = 0.03      # stagger delay between rows (seconds)
    
    svg_content = []
    svg_content.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">')
    svg_content.append('  <style>')
    svg_content.append('    text {')
    svg_content.append('      font-family: ui-monospace, SFMono-Regular, SF Mono, Consolas, "Liberation Mono", Menlo, monospace;')
    svg_content.append('      font-size: 10px;')
    svg_content.append('      white-space: pre;')
    svg_content.append('      fill: #4b5563; /* Default light theme color */')
    svg_content.append('    }')
    svg_content.append('    .cursor {')
    svg_content.append('      fill: #4b5563;')
    svg_content.append('    }')
    svg_content.append('    @media (prefers-color-scheme: dark) {')
    svg_content.append('      text {')
    svg_content.append('        fill: #9ca3af; /* Dark theme color */')
    svg_content.append('      }')
    svg_content.append('      .cursor {')
    svg_content.append('        fill: #9ca3af;')
    svg_content.append('      }')
    svg_content.append('    }')
    svg_content.append('  </style>')
    
    # Clip paths for the horizontal wipe (typing effect)
    svg_content.append('  <defs>')
    for i in range(rows):
        y_pos = i * char_height + 4.0
        start_time = i * row_stagger
        # Check if STATIC environment variable is set
        if os.environ.get("STATIC") == "1":
            svg_content.append(f'    <clipPath id="clip-{i}">')
            svg_content.append(f'      <rect x="0" y="{y_pos}" width="{svg_width}" height="{char_height}" />')
            svg_content.append(f'    </clipPath>')
        else:
            svg_content.append(f'    <clipPath id="clip-{i}">')
            svg_content.append(f'      <rect x="0" y="{y_pos}" width="0" height="{char_height}">')
            svg_content.append(f'        <animate attributeName="width" from="0" to="{svg_width}" dur="{row_duration}s" begin="{start_time:.3f}s" fill="freeze" />')
            svg_content.append(f'      </rect>')
            svg_content.append(f'    </clipPath>')
    svg_content.append('  </defs>')
    
    # Render rows of ASCII text with clip-path
    for i, row in enumerate(ascii_rows):
        y_pos = i * char_height + 12.0
        # Escape special XML characters
        escaped_row = row.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        svg_content.append(f'  <text x="0" y="{y_pos}" clip-path="url(#clip-{i})">{escaped_row}</text>')
        
        # Add typing cursor riding the clip edge (skip if STATIC)
        if os.environ.get("STATIC") != "1":
            start_time = i * row_stagger
            cursor_y = i * char_height + 4.0
            # Cursor rect moves x from 0 to svg_width
            svg_content.append(f'  <rect class="cursor" x="0" y="{cursor_y}" width="{char_width}" height="{char_height}" opacity="0">')
            svg_content.append(f'    <animate attributeName="x" from="0" to="{svg_width}" dur="{row_duration}s" begin="{start_time:.3f}s" fill="freeze" />')
            svg_content.append(f'    <animate attributeName="opacity" values="1;1;0" keyTimes="0;0.95;1" dur="{row_duration}s" begin="{start_time:.3f}s" fill="freeze" />')
            svg_content.append(f'  </rect>')
            
    svg_content.append('</svg>')
    
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(svg_content))
    print(f"Successfully generated ASCII SVG at '{svg_path}'")

if __name__ == "__main__":
    img_in = "source-prepped.png"
    svg_out = "avi-ascii.svg"
    
    if len(sys.argv) > 1:
        img_in = sys.argv[1]
    if len(sys.argv) > 2:
        svg_out = sys.argv[2]
        
    generate_ascii_svg(img_in, svg_out)
