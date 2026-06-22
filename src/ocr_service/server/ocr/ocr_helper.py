import logging
from typing import Dict, List, Optional
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
from bs4 import BeautifulSoup
import cv2
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def images_to_bytes_list(images: List[np.ndarray]) -> List[bytes]:
    """将 List[np.ndarray] 转换为 List[bytes]（PNG 格式）"""
    bytes_list = []
    for img in images:
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        _, encoded = cv2.imencode(".png", img_bgr)
        bytes_list.append(encoded.tobytes())
    return bytes_list


def _convert_pdf_to_images(pdf_path: str, dpi: int, max_workers: int = 4) -> List[np.ndarray]:
    """将PDF转换为图片列表"""
    try:
        doc = fitz.open(pdf_path)
        total_pages = doc.page_count
        doc.close()

        if total_pages == 0:
            return []
        images = []
        doc = fitz.open(pdf_path)
        for page_num in range(total_pages):
            page = doc.load_page(page_num)
            zoom = dpi / 72.0
            matrix = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=matrix)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            images.append(np.array(img))
        doc.close()
        return images
    except Exception as e:
        logger.error(f"PDF转换失败: {e}")
        return []


def html_table_to_markdown(html_table):
    """
    把 RapidDoc 输出的 <table> 表格 转成 标准 Markdown 表格
    支持 rowspan / colspan 合并单元格
    """
    soup = BeautifulSoup(html_table, "html.parser")
    table = soup.find("table")
    if not table:
        return ""

    rows = table.find_all("tr")
    if len(rows) < 1:
        return ""

    row_span_map = []
    table_data = []

    for tr in rows:
        cells = tr.find_all(["td", "th"])
        current_row = []
        col_idx = 0

        while col_idx < len(row_span_map) and row_span_map[col_idx] > 0:
            current_row.append(table_data[-1][col_idx])
            row_span_map[col_idx] -= 1
            col_idx += 1

        for cell in cells:
            text = cell.get_text(strip=True)
            colspan = int(cell.get("colspan", 1))
            rowspan = int(cell.get("rowspan", 1))

            for _ in range(colspan):
                current_row.append(text)
                if rowspan > 1:
                    while len(row_span_map) <= col_idx:
                        row_span_map.append(0)
                    row_span_map[col_idx] = rowspan - 1
                col_idx += 1

        table_data.append(current_row)

    md = []
    for i, row in enumerate(table_data):
        line = "| " + " | ".join(row) + " |"
        md.append(line)
        if i == 0:
            md.append("|" + "|".join(["---"] * len(row)) + "|")

    return "\n".join(md)


def clean_html_tables_in_text(text):
    """转换表格（自动识别 <table>...</table> 并替换为 Markdown）"""
    table_pattern = re.compile(r"<table.*?</table>", re.DOTALL)
    return table_pattern.sub(lambda m: html_table_to_markdown(m.group(0)), text)
