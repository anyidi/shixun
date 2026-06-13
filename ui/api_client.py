"""
API Client

前端调用后端 API 的客户端。
"""

import os
import requests
from typing import Optional, Tuple, List


class APIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url

    def translate(self, image_path: str, use_gpu: bool = True) -> Tuple[bool, str, str]:
        """调用翻译 API"""
        try:
            with open(image_path, "rb") as f:
                files = {"file": f}
                params = {"use_gpu": use_gpu}
                response = requests.post(f"{self.base_url}/api/translate", files=files, params=params, timeout=300)

            if response.status_code == 200:
                data = response.json()
                return True, data["result_path"], ""
            else:
                return False, "", f"API错误: {response.status_code}"
        except Exception as e:
            return False, "", f"连接失败: {str(e)}"

    def translate_batch(self, image_paths: List[str], use_gpu: bool = True) -> List[dict]:
        """批量翻译"""
        try:
            files = [("files", (os.path.basename(p), open(p, "rb"), "image/png")) for p in image_paths]
            params = {"use_gpu": use_gpu}
            response = requests.post(f"{self.base_url}/api/translate/batch", files=files, params=params, timeout=600)

            for _, (_, f, _) in files:
                f.close()

            if response.status_code == 200:
                return response.json()["results"]
            else:
                return [{"success": False, "error": f"API错误: {response.status_code}"}]
        except Exception as e:
            return [{"success": False, "error": f"连接失败: {str(e)}"}]

    def get_config(self) -> Tuple[bool, str]:
        """获取配置"""
        try:
            response = requests.get(f"{self.base_url}/api/config", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data["has_config"], data.get("app_id", "")
            return False, ""
        except:
            return False, ""

    def update_config(self, app_id: str, secret_key: str) -> bool:
        """更新配置"""
        try:
            response = requests.post(
                f"{self.base_url}/api/config",
                json={"app_id": app_id, "secret_key": secret_key},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
