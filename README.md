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
├── plugins/            # 插件目录
├── main.py             # 主程序
└── run.bat             # 启动脚本
```
