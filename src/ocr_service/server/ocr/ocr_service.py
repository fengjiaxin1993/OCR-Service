"""
RapidDoc 服务 - 支持并发限制
提供 PDF 解析 API，返回 OCR 结果和 bbox 信息
"""
import fitz  # PyMuPDF
import asyncio
import gc
import logging
import os
import time
from typing import Optional, List, Dict, Any
from fastapi import Body
from fastapi.responses import JSONResponse
from rapid_doc import RapidDocOutput

from ocr_service.server.ocr.ocr_extract_utils import handle_rapidDocOutputs
from ocr_service.server.ocr.ocr_helper import _convert_pdf_to_images, images_to_bytes_list
from ocr_service.server.ocr.single_ocr_engine import get_rapid_doc_engine
from ocr_service.settings import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RAPID_DOC_MAX_CONCURRENT = Settings.basic_settings.MAX_OCR_CONCURRENT_NUM
DPI = Settings.basic_settings.PDF_DPI

# 并发限制信号量
rapid_doc_semaphore = asyncio.Semaphore(RAPID_DOC_MAX_CONCURRENT)


async def startup_event():
    """启动时预热模型"""
    logger.info("服务启动，开始预热模型...")
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


def _ocr_pages_in_batches(bytes_list: List[bytes], total_pages: int) -> List[RapidDocOutput]:
    """
    分批调用 RapidDoc，避免一次性把所有页面塞入内存导致 OOM。
    每批处理1页，处理完释放中间数据再继续下一批。
    """
    engine = get_rapid_doc_engine()
    all_outputs = []

    for idx in range(0, total_pages):
        batch = bytes_list[idx]
        logger.info(
            f"OCR 分页处理: 第 {idx + 1} 页 / 共 {total_pages} 页"
        )

        batch_outputs = engine(inputs=batch, start_page_id=0, end_page_id=0)
        all_outputs.append(batch_outputs)
    return all_outputs


async def pdf2info(
        file_path: Optional[str] = Body(None, embed=True, description="文件路径")
):
    """
    上传 PDF 文件并解析

    - **file**: PDF 文件
    - **return_markdown**: 是否返回 Markdown
    """
    file_name = os.path.basename(file_path)
    total_pages = 0
    with fitz.open(file_path) as doc:
        total_pages = doc.page_count

    logger.info(f"调用pdf2info方法, file_name:{file_name}, 总页数:{total_pages}")
    result = {
        "success": False,
        "processing_time": 0.0,
        "markdown_text": "",
        "locate_json_result": {},
        "structure_json_result": {},
        "error": ""
    }

    if not os.path.exists(file_path):
        result["error"] = f"文件不存在: {file_path}"
        return JSONResponse(content=result)

    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext != '.pdf':
        result["error"] = f"不支持该文件格式: {file_path}"
        return JSONResponse(content=result)

    start_time = time.time()
    # 步骤1: PDF 转图片
    images = _convert_pdf_to_images(file_path, dpi=DPI)
    if not images:
        result["error"] = "PDF 转换图片失败"
        return result

    bytes_list = images_to_bytes_list(images)
    del images
    gc.collect()

    async with rapid_doc_semaphore:
        try:
            # 步骤2: 分批调用 RapidDoc
            outputs = _ocr_pages_in_batches(bytes_list, total_pages)

            del bytes_list
            gc.collect()

            # 步骤3: 合并结果
            res_dic = handle_rapidDocOutputs(outputs)

            result["success"] = True
            result["processing_time"] = time.time() - start_time
            result["markdown_text"] = res_dic["markdown"]
            result["locate_json_result"] = res_dic["layoutParsingResults"]
            result["structure_json_result"] = res_dic["structureJsonResults"]
            logger.info(
                f"pdf2info处理完成，文件: {file_name}, "
                f"页数: {total_pages}, 耗时: {result['processing_time']:.2f}秒"
            )
            return JSONResponse(content=result)
        except Exception as e:
            logger.error(f"处理文件失败: {e}")
            result["error"] = str(e)
            return JSONResponse(content=result)
