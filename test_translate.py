import sys
import os

# 设置环境变量
os.environ["BAIDU_APP_ID"] = "20260612002630702"
os.environ["BAIDU_SECRET_KEY"] = "Jat4OA2H5MxLlHYHKPDg"

from core.translator_wrapper import TranslatorWrapper

print("开始测试翻译...")

wrapper = TranslatorWrapper()

def progress_cb(value):
    if value is not None:
        print(f"进度: {value}%")

def status_cb(msg):
    if msg:
        print(f"状态: {msg}")

wrapper.set_progress_callback(progress_cb)
wrapper.set_status_callback(status_cb)

# 测试翻译
test_image = r"C:\Users\惠普\Desktop\mimg\qq_pic_merged_1781182846671.jpg"

if os.path.exists(test_image):
    print(f"翻译图片: {test_image}")
    success, result_path, error = wrapper.translate_image(test_image, use_gpu=True)

    if success:
        print(f"\n✓ 翻译成功！")
        print(f"结果: {result_path}")
    else:
        print(f"\n✗ 翻译失败: {error}")
else:
    print(f"测试图片不存在: {test_image}")
