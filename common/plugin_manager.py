import os
import json


def get_plugins(plugins_dir):
    plugins = []
    if os.path.exists(plugins_dir):
        for name in os.listdir(plugins_dir):
            plugin_path = os.path.join(plugins_dir, name)
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


def run_plugin(plugins_dir, plugin_name):
    plugin_path = os.path.join(plugins_dir, plugin_name)
    main_js = os.path.join(plugin_path, 'main.js')
    if os.path.exists(main_js):
        print(f'执行插件: {plugin_name}')
        return f'执行插件: {plugin_name}'
    return None
