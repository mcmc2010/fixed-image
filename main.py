import webview
import os
import json
import base64
import hashlib
import threading
import numpy as np
from io import BytesIO
from PIL import Image
from bottle import Bottle, static_file
from common import remove_background, feather_image, get_plugins, run_plugin

class Api:
    def __init__(self):
        self._window = None
        self._cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'caches')
        self._plugins_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins')
        os.makedirs(self._cache_dir, exist_ok=True)
        self._current_md5 = None

    def set_window(self, window):
        self._window = window

    def get_plugins(self):
        return get_plugins(self._plugins_dir)

    def check_file_exists(self, file_path):
        return os.path.exists(file_path)

    def run_plugin(self, plugin_name):
        return run_plugin(self._plugins_dir, plugin_name)

    def open_file(self):
        result = self._window.create_file_dialog(
            webview.FileDialog.OPEN,
            allow_multiple=False,
            file_types=('图片文件 (*.jpg;*.jpeg;*.png;*.webp)', '所有文件 (*.*)')
        )
        if result:
            file_path = result[0]
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            md5 = hashlib.md5(raw_data).hexdigest()
            cache_path = os.path.join(self._cache_dir, md5 + '.png')
            if not os.path.exists(cache_path):
                img = Image.open(BytesIO(raw_data))
                img.save(cache_path, 'PNG')
            self._current_md5 = md5
            return {'path': file_path, 'data': 'http://127.0.0.1:39090/images/' + md5 + '.png'}
        return None

    def close(self):
        self._window.destroy()

    def export_file(self, data_url, current_path=''):
        save_dir = os.path.dirname(current_path) if current_path else ''
        save_name = os.path.basename(current_path) if current_path else ''
        result = self._window.create_file_dialog(
            webview.FileDialog.SAVE,
            directory=save_dir,
            save_filename=save_name,
            file_types=('JPEG (*.jpg)', 'PNG (*.png)', 'WEBP (*.webp)')
        )
        if result:
            file_path = result[0]
            ext = os.path.splitext(file_path)[1].lower()
            if not ext:
                file_path += '.png'
                ext = '.png'
            if os.path.exists(file_path):
                confirm = self._window.create_confirmation_dialog('确认覆盖', f'文件已存在，是否覆盖？\n{file_path}')
                if not confirm:
                    return None
            return file_path
        return None

    def do_export(self, image_src, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if image_src.startswith('http://127.0.0.1:39090/images/'):
            md5 = image_src.split('/')[-1].replace('.png', '')
            cache_path = os.path.join(self._cache_dir, md5 + '.png')
            img = Image.open(cache_path)
        else:
            header, encoded = image_src.split(',', 1)
            img_data = base64.b64decode(encoded)
            img = Image.open(BytesIO(img_data))
        if ext in ('.jpg', '.jpeg'):
            img = img.convert('RGB')
            img.save(file_path, 'JPEG', quality=95)
        elif ext == '.png':
            img.save(file_path, 'PNG')
        elif ext == '.webp':
            img.save(file_path, 'WEBP', quality=95)
        return file_path

    def get_export_path(self, current_path=''):
        save_dir = os.path.dirname(current_path) if current_path else ''
        save_name = os.path.basename(current_path) if current_path else ''
        result = self._window.create_file_dialog(
            webview.FileDialog.SAVE,
            directory=save_dir,
            save_filename=save_name,
            file_types=('JPEG (*.jpg)', 'PNG (*.png)', 'WEBP (*.webp)')
        )
        if result:
            file_path = result[0]
            ext = os.path.splitext(file_path)[1].lower()
            if not ext:
                file_path += '.png'
            return file_path
        return None

    def export_selection(self, data_url, current_path='', x=0, y=0, w=0, h=0):
        save_dir = os.path.dirname(current_path) if current_path else ''
        if current_path:
            base_name = os.path.splitext(os.path.basename(current_path))[0]
            save_name = base_name + '_clip'
        else:
            save_name = 'clip'
        result = self._window.create_file_dialog(
            webview.FileDialog.SAVE,
            directory=save_dir,
            save_filename=save_name,
            file_types=('JPEG (*.jpg)', 'PNG (*.png)', 'WEBP (*.webp)')
        )
        if result:
            file_path = result[0]
            ext = os.path.splitext(file_path)[1].lower()
            if not ext:
                file_path += '.png'
                ext = '.png'
            if os.path.exists(file_path):
                confirm = self._window.create_confirmation_dialog('确认覆盖', f'文件已存在，是否覆盖？\n{file_path}')
                if not confirm:
                    return None
            header, encoded = data_url.split(',', 1)
            img_data = base64.b64decode(encoded)
            img = Image.open(BytesIO(img_data))
            img_w, img_h = img.size
            x = max(0, min(x, img_w))
            y = max(0, min(y, img_h))
            w = min(w, img_w - x)
            h = min(h, img_h - y)
            cropped = img.crop((x, y, x + w, y + h))
            if ext in ('.jpg', '.jpeg'):
                cropped = cropped.convert('RGB')
                cropped.save(file_path, 'JPEG', quality=95)
            elif ext == '.png':
                cropped.save(file_path, 'PNG')
            elif ext == '.webp':
                cropped.save(file_path, 'WEBP', quality=95)
            return file_path
        return None

    def do_export_selection(self, image_src, file_path, x=0, y=0, w=0, h=0):
        ext = os.path.splitext(file_path)[1].lower()
        if image_src.startswith('http://127.0.0.1:39090/images/'):
            md5 = image_src.split('/')[-1].replace('.png', '')
            cache_path = os.path.join(self._cache_dir, md5 + '.png')
            img = Image.open(cache_path)
        else:
            header, encoded = image_src.split(',', 1)
            img_data = base64.b64decode(encoded)
            img = Image.open(BytesIO(img_data))
        img_w, img_h = img.size
        x = max(0, min(x, img_w))
        y = max(0, min(y, img_h))
        w = min(w, img_w - x)
        h = min(h, img_h - y)
        cropped = img.crop((x, y, x + w, y + h))
        if ext in ('.jpg', '.jpeg'):
            cropped = cropped.convert('RGB')
            cropped.save(file_path, 'JPEG', quality=95)
        elif ext == '.png':
            cropped.save(file_path, 'PNG')
        elif ext == '.webp':
            cropped.save(file_path, 'WEBP', quality=95)
        return file_path

    def resize_image(self, image_src, width, height):
        if image_src.startswith('http://127.0.0.1:39090/images/'):
            md5 = image_src.split('/')[-1].replace('.png', '')
            cache_path = os.path.join(self._cache_dir, md5 + '.png')
            img = Image.open(cache_path)
        else:
            header, encoded = image_src.split(',', 1)
            img_data = base64.b64decode(encoded)
            img = Image.open(BytesIO(img_data))
        img = img.resize((width, height), Image.LANCZOS)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        new_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return 'data:image/png;base64,' + new_data

    def restore_original(self):
        if self._current_md5:
            cache_path = os.path.join(self._cache_dir, self._current_md5 + '.png')
            if os.path.exists(cache_path):
                return 'http://127.0.0.1:39090/images/' + self._current_md5 + '.png'
        return None

    def remove_background(self, image_src, color_hex, tolerance=10):
        return remove_background(image_src, self._cache_dir, color_hex, tolerance)

    def feather_image(self, image_src, radius=10, blur=3):
        return feather_image(image_src, self._cache_dir, radius, blur)

base_dir = os.path.dirname(os.path.abspath(__file__))
cache_dir = os.path.join(base_dir, 'caches')
html_path = os.path.join(base_dir, "app", "index.html")

app = Bottle()

@app.route('/images/<filename>')
def serve_image(filename):
    print(f'Serve: Image -> {filename}')
    return static_file(filename, root=cache_dir)

def start_image_server():
    app.run(host='127.0.0.1', port=39090, quiet=True)

api = Api()
window = webview.create_window("Fixed Image Editor", url=html_path, width=1280, height=720, min_size=(1280, 720), js_api=api)
api.set_window(window)

threading.Thread(target=start_image_server, daemon=True).start()

webview.start(gui='cef',
    # http_server=True, 
    http_port=39080,
    debug=False)
