import os
import json
import importlib.util


def get_plugins(plugins_dir):
    plugins = []
    if os.path.exists(plugins_dir):
        for name in os.listdir(plugins_dir):
            plugin_path = os.path.join(plugins_dir, name)
            if os.path.isdir(plugin_path):
                info_path = os.path.join(plugin_path, 'plugin.json')
                info = {'name': name, 'version': '', 'description': '', 'tools': []}
                if os.path.exists(info_path):
                    with open(info_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        info.update(data)
                plugins.append(info)
                print(f'已加载插件: {info["name"]} v{info["version"]}')
    return plugins


def get_tool_info(plugins_dir, plugin_name, tool_name):
    plugin_path = os.path.join(plugins_dir, plugin_name)
    info_path = os.path.join(plugin_path, 'plugin.json')
    if os.path.exists(info_path):
        with open(info_path, 'r', encoding='utf-8') as f:
            info = json.load(f)
            for tool in info.get('tools', []):
                if tool.get('name') == tool_name:
                    return tool
    return None


def run_plugin(plugins_dir, plugin_name):
    plugin_path = os.path.join(plugins_dir, plugin_name)
    main_js = os.path.join(plugin_path, 'main.js')
    if os.path.exists(main_js):
        print(f'执行插件: {plugin_name}')
        return f'执行插件: {plugin_name}'
    return None


def run_plugin_tool(plugins_dir, plugin_name, tool_name, image_src=None, cache_dir=None, params=None):
    plugin_path = os.path.join(plugins_dir, plugin_name)
    
    info_path = os.path.join(plugin_path, 'plugin.json')
    if os.path.exists(info_path):
        with open(info_path, 'r', encoding='utf-8') as f:
            info = json.load(f)
            for tool in info.get('tools', []):
                if tool.get('name') == tool_name:
                    script = tool.get('script')
                    if script:
                        script_path = os.path.join(plugin_path, script)
                        if os.path.exists(script_path):
                            spec = importlib.util.spec_from_file_location("plugin_tool", script_path)
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            if hasattr(module, 'run'):
                                if params is None:
                                    params = {}
                                result = module.run(image_src, cache_dir, **params)
                                print(f'执行: {plugin_name} - {tool_name}')
                                return result
    
    return None
