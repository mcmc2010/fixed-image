import webview
import os
import json
import base64
from io import BytesIO
from PIL import Image

class Api:
    def __init__(self):
        self._window = None
        self._cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'caches')
        self._plugins_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins')
        os.makedirs(self._cache_dir, exist_ok=True)
        self._original_data = None

    def set_window(self, window):
        self._window = window

    def get_plugins(self):
        plugins = []
        if os.path.exists(self._plugins_dir):
            for name in os.listdir(self._plugins_dir):
                plugin_path = os.path.join(self._plugins_dir, name)
                if os.path.isdir(plugin_path):
                    info_path = os.path.join(plugin_path, 'plugin.json')
                    info = {'name': name, 'version': '', 'description': ''}
                    if os.path.exists(info_path):
                        with open(info_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            info.update(data)
                    plugins.append(info)
                    print(f'已加载插件: {info["name"]} v{info["version"]}')
        return plugins

    def check_file_exists(self, file_path):
        return os.path.exists(file_path)

    def run_plugin(self, plugin_name):
        plugin_path = os.path.join(self._plugins_dir, plugin_name)
        main_js = os.path.join(plugin_path, 'main.js')
        if os.path.exists(main_js):
            print(f'执行插件: {plugin_name}')
            return f'执行插件: {plugin_name}'
        return None

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
            self._original_data = raw_data
            data = base64.b64encode(raw_data).decode('utf-8')
            ext = os.path.splitext(file_path)[1].lower()
            mime_map = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp'}
            mime = mime_map.get(ext, 'image/png')
            return {'path': file_path, 'data': 'data:' + mime + ';base64,' + data}
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

    def do_export(self, data_url, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        header, encoded = data_url.split(',', 1)
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

    def do_export_selection(self, data_url, file_path, x=0, y=0, w=0, h=0):
        ext = os.path.splitext(file_path)[1].lower()
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

    def resize_image(self, data_url, width, height):
        header, encoded = data_url.split(',', 1)
        img_data = base64.b64decode(encoded)
        img = Image.open(BytesIO(img_data))
        img = img.resize((width, height), Image.LANCZOS)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        new_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return 'data:image/png;base64,' + new_data

    def restore_original(self):
        if self._original_data:
            data = base64.b64encode(self._original_data).decode('utf-8')
            return 'data:image/png;base64,' + data
        return None

base_dir = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(base_dir, "app", "index.html")

api = Api()
window = webview.create_window("Fixed Image Editor", url=html_path, width=1280, height=720, min_size=(1280, 720), js_api=api)
api.set_window(window)

webview.start(gui='cef',
    # http_server=True, 
    http_port=39080,      # 固定端口
    debug=False)
