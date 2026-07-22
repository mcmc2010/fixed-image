import os
import numpy as np
from PIL import Image
from io import BytesIO
import base64
from scipy import ndimage


def remove_background(image_src, cache_dir, color_hex, tolerance=10):
    if image_src.startswith('http://127.0.0.1:39090/images/'):
        md5 = image_src.split('/')[-1].replace('.png', '')
        cache_path = os.path.join(cache_dir, md5 + '.png')
        img = Image.open(cache_path).convert('RGBA')
    else:
        header, encoded = image_src.split(',', 1)
        img_data = base64.b64decode(encoded)
        img = Image.open(BytesIO(img_data)).convert('RGBA')
    
    r_target = int(color_hex[1:3], 16)
    g_target = int(color_hex[3:5], 16)
    b_target = int(color_hex[5:7], 16)
    
    data = np.array(img)
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    
    diff = np.sqrt((r.astype(int) - r_target)**2 + 
                   (g.astype(int) - g_target)**2 + 
                   (b.astype(int) - b_target)**2)
    
    mask = diff <= tolerance
    data[mask, 3] = 0
    
    result = Image.fromarray(data)
    buffer = BytesIO()
    result.save(buffer, format='PNG')
    new_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return 'data:image/png;base64,' + new_data


def feather_image(image_src, cache_dir, radius=10, blur=3):
    if image_src.startswith('http://127.0.0.1:39090/images/'):
        md5 = image_src.split('/')[-1].replace('.png', '')
        cache_path = os.path.join(cache_dir, md5 + '.png')
        img = Image.open(cache_path).convert('RGBA')
    else:
        header, encoded = image_src.split(',', 1)
        img_data = base64.b64decode(encoded)
        img = Image.open(BytesIO(img_data)).convert('RGBA')
    
    data = np.array(img)
    alpha = data[:,:,3].astype(float)
    
    dist = ndimage.distance_transform_edt(alpha > 0)
    
    feather = np.clip(dist / radius, 0, 1)
    alpha = alpha * feather
    
    if blur > 0:
        alpha = ndimage.gaussian_filter(alpha, sigma=blur)
    
    data[:,:,3] = alpha.astype(np.uint8)
    
    result = Image.fromarray(data)
    buffer = BytesIO()
    result.save(buffer, format='PNG')
    new_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return 'data:image/png;base64,' + new_data
