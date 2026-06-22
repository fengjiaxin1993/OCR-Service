from fastapi import APIRouter
from ocr_service.server.ocr.ocr_service import health_check, pdf2info

ocr_router = APIRouter(prefix="/api", tags=["OCR文件识别"])


ocr_router.get(
    "/health",
    summary="健康检查",
    description="""健康检查""",
)(health_check)

ocr_router.post(
    "/parse/pdf2info",
    summary="PDF提取信息",
    description="""PDF提取信息""",
)(pdf2info)
