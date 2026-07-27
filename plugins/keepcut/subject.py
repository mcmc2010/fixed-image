import numpy as np
from PIL import Image
from scipy import ndimage
from io import BytesIO
import base64
import os
from collections import Counter


def get_corner_color(rgb, h, w, sample_size=10):
    corners = np.vstack([
        rgb[0:sample_size, 0:sample_size].reshape(-1, 3),
        rgb[0:sample_size, w-sample_size:w].reshape(-1, 3),
        rgb[h-sample_size:h, 0:sample_size].reshape(-1, 3),
        rgb[h-sample_size:h, w-sample_size:w].reshape(-1, 3)
    ])
    
    quantized = (corners // 10) * 10
    unique_colors, counts = np.unique(quantized, axis=0, return_counts=True)
    bg_color = unique_colors[np.argmax(counts)] + 5
    
    return tuple(bg_color.astype(int))


def run(image_src, cache_dir, tolerance=30, mode='auto', color='#ffffff'):
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
    
    if mode == 'auto':
        detected = get_corner_color(rgb, h, w)
        r_target, g_target, b_target = detected
        detected_hex = '#{:02x}{:02x}{:02x}'.format(r_target, g_target, b_target)
    else:
        r_target = int(color[1:3], 16)
        g_target = int(color[3:5], 16)
        b_target = int(color[5:7], 16)
        detected_hex = color
    
    visited = np.zeros((h, w), dtype=bool)
    mask = np.zeros((h, w), dtype=bool)
    
    corners = [(0, 0), (0, w-1), (h-1, 0), (h-1, w-1)]
    
    for y, x in corners:
        if visited[y, x]:
            continue
        
        stack = [(y, x)]
        
        while stack:
            cy, cx = stack.pop()
            
            if visited[cy, cx]:
                continue
            
            diff = np.sqrt((rgb[cy, cx, 0] - r_target)**2 + 
                          (rgb[cy, cx, 1] - g_target)**2 + 
                          (rgb[cy, cx, 2] - b_target)**2)
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
        'mask_url': 'http://127.0.0.1:39090/images/' + md5 + '_mask.png',
        'detected_color': detected_hex
    }
