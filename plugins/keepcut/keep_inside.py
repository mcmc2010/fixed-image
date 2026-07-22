import numpy as np
from PIL import Image
from io import BytesIO
import base64
import os


def run(image_src, cache_dir):
    if image_src.startswith('http://127.0.0.1:39090/images/'):
        md5 = image_src.split('/')[-1].replace('.png', '')
        cache_path = os.path.join(cache_dir, md5 + '.png')
        mask_path = os.path.join(cache_dir, md5 + '_mask.png')
    else:
        return None
    
    if not os.path.exists(mask_path):
        print('蒙版不存在，请先执行 Subject')
        return None
    
    img = Image.open(cache_path).convert('RGBA')
    mask = Image.open(mask_path).convert('RGBA')
    
    data = np.array(img)
    mask_data = np.array(mask)
    
    subject_mask = mask_data[:,:,3] > 128
    
    alpha = data[:,:,3].astype(float)
    alpha = alpha * subject_mask.astype(float)
    data[:,:,3] = alpha.astype(np.uint8)
    
    result = Image.fromarray(data)
    result_path = os.path.join(cache_dir, md5 + '_result.png')
    result.save(result_path, 'PNG')
    
    return 'http://127.0.0.1:39090/images/' + md5 + '_result.png'
