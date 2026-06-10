# 识别pdf扫描件 markdown格式的服务
"""
RapidDoc 服务 - 支持并发限制为 3
提供 PDF 解析 API，返回 OCR 结果和 bbox 信息
"""

import asyncio
import json
import logging
import os
import time
from typing import Optional, List, Dict, Any
from fastapi import Body
from fastapi.responses import JSONResponse
from server.ocr.ocr_extract_utils import handle_rapidDocOutputs, images_to_bytes_list
from server.ocr.ocr_helper import _convert_pdf_to_images
from server.ocr.single_ocr_engine import get_rapid_doc_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== 全局配置 ====================

# 从环境变量读取配置，如果没有则使用默认值
RAPID_DOC_MAX_CONCURRENT = int(os.environ.get("RAPID_DOC_MAX_CONCURRENT", "2"))
DPI = int(os.environ.get("DPI", "200"))

# 并发限制信号量
rapid_doc_semaphore = asyncio.Semaphore(RAPID_DOC_MAX_CONCURRENT)


async def startup_event():
    """启动时预热模型"""
    logger.info("服务启动，开始预热模型...")
    # 同步等待预热完成，确保服务启动后再接收请求
    await preload_model()
    logger.info("模型预热完成，服务已就绪")


async def preload_model():
    """预热模型（在后台运行）"""
    try:
        get_rapid_doc_engine()
        logger.info("模型预热完成")
    except Exception as e:
        logger.error(f"模型预热失败: {e}")


async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "RAPID_DOC_MAX_CONCURRENT": RAPID_DOC_MAX_CONCURRENT,
        "DPI": DPI
    }


async def pdf2info(
        file_path: Optional[str] = Body(None, embed=True, description="文件路径")
):
    """
    上传 PDF 文件并解析

    - **file**: PDF 文件
    - **return_markdown**: 是否返回 Markdown
    """
    logger.info(f"调用pdf2md方法, file_path:{file_path}")
    filename = os.path.basename(file_path)
    # 获取信号量（限制并发）
    result = {
        "success": False,
        "processing_time": 0.0,
        "filename": filename,
        "filepath": file_path,
        "markdown": "",
        "layoutParsingResults": "",
        "structureJsonResults": ""
    }

    if not os.path.exists(file_path):
        result["error"] = f"文件不存在: {file_path}"
        return JSONResponse(content=result)

    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext != '.pdf':
        result["error"] = f"不支持该文件格式: {file_path}"
        return JSONResponse(content=result)
    images = _convert_pdf_to_images(file_path, dpi=200)
    bytes_list = images_to_bytes_list(images)

    async with rapid_doc_semaphore:
        start_time = time.time()
        try:
            # 保存上传的文件到临时文件

            # 调用 RapidDoc 解析
            engine = get_rapid_doc_engine()
            outputs = engine(inputs=bytes_list)
            res_dic = handle_rapidDocOutputs(outputs)
            # 构建响应
            result["success"] = True
            result["processing_time"] = time.time() - start_time
            result["markdown"] = res_dic["markdown"]
            layoutParsingResults_str = json.dumps(res_dic["layoutParsingResults"], indent=2, ensure_ascii=False)
            structureJsonResults_str = json.dumps(res_dic["structureJsonResults"], indent=2, ensure_ascii=False)
            result["layoutParsingResults"] = layoutParsingResults_str
            result["structureJsonResults"] = structureJsonResults_str
            logger.info(f"pdf2md处理完成， 文件: {filename}, 耗时: {result['processing_time']:.2f}秒")
            return JSONResponse(content=result)

        except Exception as e:
            logger.error(f"处理文件失败: {e}")
            result["error"] = str(e)
            return JSONResponse(content=result)