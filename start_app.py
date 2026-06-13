"""
启动脚本 - 前后端分离模式

先启动后端 API 服务器，再启动前端客户端。
"""

import subprocess
import sys
import time
import os

def start_backend():
    """启动后端服务"""
    print("启动后端 API 服务器...")
    backend_process = subprocess.Popen(
        [sys.executable, "backend/api_server.py"],
        cwd=os.path.dirname(__file__)
    )
    time.sleep(2)  # 等待后端启动
    return backend_process

def start_frontend():
    """启动前端客户端"""
    print("启动前端客户端...")
    subprocess.run([sys.executable, "main.py"])

if __name__ == "__main__":
    backend_proc = None
    try:
        backend_proc = start_backend()
        start_frontend()
    except KeyboardInterrupt:
        print("\n正在关闭...")
    finally:
        if backend_proc:
            backend_proc.terminate()
            backend_proc.wait()
