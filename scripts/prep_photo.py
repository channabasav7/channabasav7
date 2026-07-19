import sys
import os
import cv2
import numpy as np
from rembg import remove
from PIL import Image

def prep_photo(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} does not exist.")
        sys.exit(1)
        
    print(f"Loading image '{input_path}'...")
    img_pil = Image.open(input_path)
    
    print("Removing background using rembg (this might take a moment on first run to download model)...")
    try:
        no_bg_pil = remove(img_pil)
    except Exception as e:
        print(f"Warning: Background removal failed: {e}. Proceeding without background removal.")
        no_bg_pil = img_pil
        
    # Convert PIL image to NumPy array (RGBA)
    no_bg_np = np.array(no_bg_pil.convert("RGBA"))
    
    # Extract RGB and Alpha channels
    # PIL loads RGB, so NumPy array is RGBA. OpenCV uses BGRA.
    # Convert RGB to BGR
    r, g, b, alpha = no_bg_np[:,:,0], no_bg_np[:,:,1], no_bg_np[:,:,2], no_bg_np[:,:,3]
    bgr = cv2.merge((b, g, r))
    
    print("Applying CLAHE for local contrast enhancement...")
    # Convert to LAB color space
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    l, a_channel, b_channel = cv2.split(lab)
    
    # Create CLAHE object
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)
    
    # Merge channels back and convert to BGR
    enhanced_lab = cv2.merge((l_enhanced, a_channel, b_channel))
    enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    
    # Create a pure white background
    white_bg = np.ones_like(enhanced_bgr) * 255
    
    # Normalize alpha mask to [0, 1]
    mask = alpha[:, :, np.newaxis] / 255.0
    
    # Composite foreground onto white background
    composited = (enhanced_bgr * mask + white_bg * (1.0 - mask)).astype(np.uint8)
    
    # Convert to grayscale
    gray = cv2.cvtColor(composited, cv2.COLOR_BGR2GRAY)
    
    # Save the output image
    cv2.imwrite(output_path, gray)
    print(f"Successfully prepped photo and saved to '{output_path}'")

if __name__ == "__main__":
    input_file = "source-photo.jpg"
    output_file = "source-prepped.png"
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
        
    prep_photo(input_file, output_file)
