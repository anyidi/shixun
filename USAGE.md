# 漫画翻译器 - 使用说明

## 项目概述

基于 manga-image-translator 的 PyQt6 桌面应用，实现日文漫画图片翻译成中文。

## 项目特点

1. **保持原项目架构**：直接调用 manga-image-translator 的核心翻译逻辑，不修改原有功能
2. **使用百度翻译**：配置百度翻译 API 进行在线翻译
3. **简洁美观的界面**：扁平化设计，无渐变色，清晰直观
4. **异步处理**：使用 QThread 避免 UI 冻结
5. **配置管理**：自动保存用户设置和 API 密钥

## 项目结构

```
F:\6176\
├── main.py                    # 应用入口
├── config.json               # 翻译器配置（百度翻译）
├── requirements.txt          # Python 依赖
├── README.md                 # 项目说明
├── PLAN.md                   # 实现计划
├── USAGE.md                  # 使用说明（本文件）
├── core/                     # 核心模块
│   ├── __init__.py
│   ├── translator_wrapper.py  # 翻译器封装
│   └── config_manager.py      # 配置管理
├── ui/                       # 界面模块
│   ├── __init__.py
│   └── main_window.py        # 主窗口
└── resources/                # 资源文件
    └── styles.qss            # 样式表
```

## 安装步骤

### 1. 确保依赖已安装

本应用依赖于 manga-image-translator 项目，确保其已正确安装：

```bash
cd f:\shixun\manga-image-translator
pip install -r requirements.txt
```

### 2. 安装 PyQt6

```bash
cd F:\6176
pip install -r requirements.txt
```

或手动安装：
```bash
pip install PyQt6 Pillow
```

### 3. 配置百度翻译 API

首次运行时会提示配置 API 密钥，也可以手动配置：

1. 访问 https://fanyi-api.baidu.com/
2. 注册并创建应用
3. 获取 APP ID 和密钥
4. 在应用设置中输入

配置会自动保存到：`C:\Users\你的用户名\.manga_translator\settings.json`

## 运行应用

```bash
cd F:\6176
python main.py
```

## 使用流程

### 1. 启动应用

运行 `python main.py`，会打开主窗口。

### 2. 配置 API（首次使用）

- 点击右上角"设置"按钮
- 输入百度翻译 APP ID 和密钥
- 点击"确定"保存

### 3. 选择图片

- 点击"选择图片"按钮
- 选择一张日文漫画图片（支持 JPG、PNG 等格式）
- 原图会显示在左侧预览区

### 4. 开始翻译

- 点击"开始翻译"按钮
- 等待翻译完成（进度条会显示进度）
- 翻译结果显示在右侧预览区

### 5. 保存结果

- 点击"保存结果"按钮
- 选择保存位置
- 翻译后的图片会保存为 PNG 格式

## 技术架构

### 核心组件

#### 1. TranslatorWrapper (core/translator_wrapper.py)

- 封装 `MangaTranslatorLocal` 类
- 提供同步的 `translate_image()` 方法
- 处理环境变量（百度 API 密钥）
- 支持进度和状态回调

```python
wrapper = TranslatorWrapper(baidu_app_id="...", baidu_secret="...")
success, result_path, error = wrapper.translate_image("input.jpg")
```

#### 2. ConfigManager (core/config_manager.py)

- 管理用户配置
- 保存/读取 API 密钥
- 记住上次使用的目录

```python
config = ConfigManager()
app_id, secret = config.get_baidu_credentials()
config.set_baidu_credentials(app_id, secret)
```

#### 3. MainWindow (ui/main_window.py)

- 主窗口 UI
- 图片选择和显示
- 翻译进度显示
- 结果保存

#### 4. TranslatorThread

- QThread 子类
- 在后台线程运行翻译
- 通过信号更新 UI

### 翻译流程

```
用户选择图片
    ↓
点击"开始翻译"
    ↓
创建 TranslatorThread
    ↓
调用 TranslatorWrapper.translate_image()
    ↓
调用 manga-image-translator 核心库
    ├── 文本检测（Detection）
    ├── OCR 识别
    ├── 百度翻译 API
    ├── 图像修复（Inpainting）
    └── 文字渲染（Rendering）
    ↓
返回翻译结果
    ↓
显示在 UI 上
```

## 配置文件说明

### config.json

翻译器配置，与 manga-image-translator 兼容：

```json
{
  "translator": {
    "translator": "baidu",
    "target_lang": "CHS"
  },
  "detector": {
    "detector": "default",
    "detection_size": 2048
  },
  "ocr": {
    "ocr": "48px"
  },
  "inpainter": {
    "inpainter": "lama_large"
  }
}
```

### settings.json

用户设置，自动生成在 `~/.manga_translator/settings.json`：

```json
{
  "baidu_app_id": "你的APP_ID",
  "baidu_secret_key": "你的密钥",
  "use_gpu": true,
  "last_input_dir": "",
  "last_output_dir": ""
}
```

## 界面设计

### 颜色方案（扁平化）

- 背景色：#f5f5f5（浅灰）
- 面板色：#ffffff（白色）
- 边框色：#d0d0d0（中灰）
- 主按钮：#4CAF50（绿色）
- 次按钮：#2196F3（蓝色）
- 警告按钮：#FF9800（橙色）
- 文本色：#333333（深灰）

### 布局

```
┌────────────────────────────────────────────────────────┐
│  [选择图片]  [开始翻译]  [保存结果]        [设置]     │
├────────────────────────────────────────────────────────┤
│  ┌──────────────────┐      ┌──────────────────┐       │
│  │    原图          │      │   翻译结果       │       │
│  │   (预览区)       │      │   (预览区)       │       │
│  │                  │      │                  │       │
│  └──────────────────┘      └──────────────────┘       │
├────────────────────────────────────────────────────────┤
│  进度: [████████████░░░░░░░░] 60%                     │
│  状态: 正在翻译...                                     │
└────────────────────────────────────────────────────────┘
```

## 常见问题

### 1. 翻译失败，提示"未配置百度翻译 API 密钥"

- 点击"设置"按钮配置 API 密钥
- 确保 APP ID 和密钥正确无误

### 2. 翻译速度慢

- 首次运行需要下载模型，会比较慢
- 后续翻译会快很多
- 使用 GPU 可以加速翻译

### 3. 图片预览显示不正常

- 确保图片格式支持（JPG、PNG 等）
- 检查图片是否损坏
- 尝试调整窗口大小

### 4. 翻译结果不准确

- 百度翻译对漫画对话的翻译可能不够准确
- 可以考虑切换到其他翻译器（需修改 config.json）

## 扩展开发

### 添加其他翻译器

修改 `config.json` 中的 `translator` 字段：

```json
{
  "translator": {
    "translator": "deepl",  // 或 "chatgpt", "offline" 等
    "target_lang": "CHS"
  }
}
```

需要配置相应的环境变量（如 DEEPL_API_KEY）。

### 自定义样式

修改 `resources/styles.qss` 文件，使用 Qt 样式表语法。

### 添加新功能

在 `ui/main_window.py` 中扩展 `MainWindow` 类。

## 许可证

本项目基于 manga-image-translator，遵循其开源许可证。

## 致谢

- [manga-image-translator](https://github.com/zyddnys/manga-image-translator) - 核心翻译引擎
- PyQt6 - GUI 框架
- 百度翻译 API - 翻译服务
