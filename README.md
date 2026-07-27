# Fixed Image Editor

基于 pywebview 的轻量级图片编辑器。

## 功能

- 打开图片：支持 JPG、PNG、WEBP
- 导出图片：可转换格式（JPG/PNG/WEBP）
- 选择工具：矩形选区，支持拖拽调整
- 导出选区：裁剪选区并导出
- 调整大小：自定义宽高，锁定比例
- 恢复原图：一键还原
- 缩放：放大/缩小/重置
- 变换：左右翻转、上下翻转
- 羽化：边缘渐变透明，支持高斯模糊
- 移除背景：按颜色移除纯色背景
- 插件系统：可扩展功能

## 运行

```bash
pip install -r requirements.txt
python main.py
```

或双击 `run.bat`。

## 目录结构

```
├── app/                # 前端资源
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── vendor/
├── common/             # Python 模块
│   ├── image_utils.py  # 图像处理算法
│   └── plugin_manager.py # 插件管理
├── plugins/            # 插件目录
├── caches/             # 缓存目录（自动创建）
├── main.py             # 主程序
├── requirements.txt    # Python 依赖
└── run.bat             # 启动脚本
```

## 插件开发

在 `plugins/` 目录下创建插件文件夹，包含 `plugin.json` 和脚本文件。

```json
{
    "name": "MyPlugin",
    "version": "1.0.0",
    "description": "我的插件",
    "tools": [
        {
            "name": "Tool1",
            "description": "工具描述",
            "script": "tool1.py",
            "params": [
                { "name": "param1", "label": "参数1", "type": "range", "min": 1, "max": 100, "default": 50 }
            ]
        }
    ]
}
```

脚本需实现 `run(image_src, cache_dir, **params)` 方法。
