import numpy as np
from PIL import Image
from scipy import ndimage
from io import BytesIO
import base64
import os


def run(image_src, cache_dir, tolerance=30):
    tolerance = int(tolerance)
    if image_src.startswith('http://127.0.0.1:39090/images/'):
        md5 = image_src.split('/')[-1].replace('.png', '')
        cache_path = os.path.join(cache_dir, md5 + '.png')
        img = Image.open(cache_path).convert('RGBA')
    else:
        header, encoded = image_src.split(',', 1)
        img_data = base64.b64decode(encoded)
        img = Image.open(BytesIO(img_data)).convert('RGBA')
    
    data = np.array(img)
    rgb = data[:,:,:3].astype(float)
    h, w = rgb.shape[:2]
    
    visited = np.zeros((h, w), dtype=bool)
    mask = np.zeros((h, w), dtype=bool)
    
    corners = [(0, 0), (0, w-1), (h-1, 0), (h-1, w-1)]
    
    for y, x in corners:
        if visited[y, x]:
            continue
        
        target_color = rgb[y, x]
        stack = [(y, x)]
        
        while stack:
            cy, cx = stack.pop()
            
            if visited[cy, cx]:
                continue
            
            diff = np.sqrt(np.sum((rgb[cy, cx] - target_color) ** 2))
            if diff > tolerance:
                continue
            
            visited[cy, cx] = True
            mask[cy, cx] = True
            
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                    stack.append((ny, nx))
    
    subject_mask = ~mask
    
    subject_mask = ndimage.binary_fill_holes(subject_mask)
    
    subject_mask = ndimage.binary_erosion(subject_mask, iterations=2)
    subject_mask = ndimage.binary_dilation(subject_mask, iterations=2)
    
    mask_path = os.path.join(cache_dir, md5 + '_mask.png')
    mask_data = np.zeros((h, w, 4), dtype=np.uint8)
    mask_data[subject_mask] = [255, 0, 0, 128]
    mask_data[~subject_mask] = [0, 0, 0, 0]
    mask_img = Image.fromarray(mask_data, mode='RGBA')
    mask_img.save(mask_path, 'PNG')
    
    return {
        'image': image_src,
        'mask_url': 'http://127.0.0.1:39090/images/' + md5 + '_mask.png'
    }
