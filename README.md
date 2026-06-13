# Manga Translator Desktop Application

PyQt6 桌面应用，用于将日文漫画图片翻译成中文。

## 功能特性

- 选择日文漫画图片
- 自动翻译为中文
- 显示原图和翻译结果对比
- 使用百度翻译 API
- 美观简约的界面设计

## 安装依赖

```bash
pip install PyQt6 Pillow
```

## 配置

首次运行需要配置百度翻译 API：
1. 访问 https://fanyi-api.baidu.com/ 申请 API
2. 在应用设置中输入 APP ID 和密钥

## 使用方法

```bash
python main.py
```

1. 点击"选择图片"按钮选择日文漫画图片
2. 点击"开始翻译"按钮
3. 等待翻译完成
4. 查看翻译结果并保存

## 项目结构

```
F:\6176\
├── main.py                    # 应用入口
├── config.json               # 翻译配置
├── ui/
│   ├── main_window.py        # 主窗口
│   └── widgets.py            # 自定义组件
├── core/
│   ├── translator_wrapper.py # 翻译器封装
│   └── config_manager.py     # 配置管理
└── resources/
    └── styles.qss            # 样式表
```
