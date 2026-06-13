"""
Backend API Server

FastAPI 后端服务，提供翻译 API 接口。
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import uvicorn

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.translator_wrapper import TranslatorWrapper
from core.config_manager import ConfigManager

app = FastAPI(title="漫画翻译器 API")
config_manager = ConfigManager()

# 设置环境变量
app_id, secret = config_manager.get_baidu_credentials()
if app_id:
    os.environ["BAIDU_APP_ID"] = app_id
if secret:
    os.environ["BAIDU_SECRET_KEY"] = secret


class TranslateRequest(BaseModel):
    input_path: str
    use_gpu: bool = True


class ConfigUpdate(BaseModel):
    app_id: str
    secret_key: str


@app.post("/api/translate")
async def translate(file: UploadFile = File(...), use_gpu: bool = True):
    """翻译上传的图片"""
    try:
        # 保存上传文件
        temp_dir = Path("F:/6176/temp")
        temp_dir.mkdir(exist_ok=True)

        input_path = temp_dir / file.filename
        with open(input_path, "wb") as f:
            f.write(await file.read())

        # 获取配置并确保环境变量已设置
        app_id, secret = config_manager.get_baidu_credentials()
        if not app_id or not secret:
            raise HTTPException(status_code=400, detail="请先配置百度 API 密钥")

        os.environ["BAIDU_APP_ID"] = app_id
        os.environ["BAIDU_SECRET_KEY"] = secret

        # 执行翻译
        wrapper = TranslatorWrapper(baidu_app_id=app_id, baidu_secret=secret)
        success, result_path, error = await wrapper.translate_image_async(str(input_path), use_gpu=use_gpu)

        if not success:
            raise HTTPException(status_code=500, detail=error)

        return {"success": True, "result_path": result_path}
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)
@app.post("/api/translate/batch")
async def translate_batch(files: List[UploadFile] = File(...), use_gpu: bool = True):
    """批量翻译图片"""
    try:
        temp_dir = Path("F:/6176/temp/batch")
        temp_dir.mkdir(parents=True, exist_ok=True)

        results = []
        app_id, secret = config_manager.get_baidu_credentials()
        if not app_id or not secret:
            raise HTTPException(status_code=400, detail="请先配置百度 API 密钥")

        os.environ["BAIDU_APP_ID"] = app_id
        os.environ["BAIDU_SECRET_KEY"] = secret

        wrapper = TranslatorWrapper(baidu_app_id=app_id, baidu_secret=secret)

        for idx, file in enumerate(files):
            input_path = temp_dir / f"{idx}_{file.filename}"
            with open(input_path, "wb") as f:
                f.write(await file.read())

            success, result_path, error = await wrapper.translate_image_async(str(input_path), use_gpu=use_gpu)
            results.append({
                "filename": file.filename,
                "success": success,
                "result_path": result_path if success else None,
                "error": error if not success else None
            })

        return {"results": results}
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"{str(e)}\n{traceback.format_exc()}")



async def get_result(filename: str):
    """获取翻译结果图片"""
    result_path = Path("F:/6176/temp") / filename
    if not result_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(result_path)


@app.post("/api/config")
async def update_config(config: ConfigUpdate):
    """更新百度 API 配置"""
    config_manager.set_baidu_credentials(config.app_id, config.secret_key)
    os.environ["BAIDU_APP_ID"] = config.app_id
    os.environ["BAIDU_SECRET_KEY"] = config.secret_key
    return {"success": True}


@app.get("/api/config")
async def get_config():
    """获取当前配置"""
    app_id, secret = config_manager.get_baidu_credentials()
    return {
        "has_config": bool(app_id and secret),
        "app_id": app_id if app_id else ""
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
