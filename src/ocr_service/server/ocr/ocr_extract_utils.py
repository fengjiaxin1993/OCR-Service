import logging
from typing import Dict, Any, List
from rapid_doc import RapidDocOutput

from ocr_service.server.ocr.ocr_helper import clean_html_tables_in_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_doc_id(text, res_list):
    for res in res_list:
        if text in res["text"]:
            return res["doc_id"]
    return ""


def handle_rapidDocOutputs(outputs: List[RapidDocOutput]) -> Dict[str, Any]:
    total_markdown = ""
    for idx, output in enumerate(outputs):
        total_markdown += output.markdown
        total_markdown += "\n"

    final_markdown = clean_html_tables_in_text(total_markdown)
    structure_json_result = split_markdown(final_markdown)

    layout_res_list = []
    for page_idx, output in enumerate(outputs):
        middle_json = output.middle_json
        pdf_info_list = middle_json["pdf_info"]
        pdf_info = pdf_info_list[0]
        parsing_res_list = []
        page_size = pdf_info["page_size"]
        page_width = page_size[0]
        page_height = page_size[1]
        para_blocks = pdf_info["para_blocks"]
        for para_idx, block in enumerate(para_blocks):
            block_idx = 0
            lines = block.get("lines", [])
            for line in lines:
                spans = line.get("spans", [])
                for span in spans:
                    bbox = span["bbox"]
                    content = span["content"]
                    block_type = span["type"]
                    if block_type != "text":
                        continue
                    block_id = f"block_{page_idx}_{para_idx}_{block_idx}"
                    doc_id = get_doc_id(content, structure_json_result["structure_json_result"])
                    parsing_res_list.append({
                        "block_id": block_id,
                        "block_content": content,
                        "block_type": block_type,
                        "block_bbox": bbox,
                        "doc_id": doc_id,
                    })
                    block_idx += 1
        layout_res_list.append({
            "meta": {
                "page_idx": page_idx,
                "page_width": page_width,
                "page_height": page_height,
            },
            "parsing_res_list": parsing_res_list,
        })

    res = {
        "layoutParsingResults": {"layout_res_list": layout_res_list},
        "markdown": final_markdown,
        "structureJsonResults": structure_json_result
    }
    return res


headers_to_split_on = [
    ("#", "title"),
    ("##", "title"),
    ("###", "title"),
    ("####", "title"),
]


def split_markdown(content: str) -> Dict[str, Any]:
    from langchain_text_splitters import MarkdownHeaderTextSplitter

    text_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on, strip_headers=False
    )
    docs = text_splitter.split_text(content)
    res_list = []
    for idx, doc in enumerate(docs):
        dic = {}
        text = doc.page_content
        title = doc.metadata.get("title", "")
        dic["title"] = title
        dic["text"] = text
        dic["doc_id"] = f"doc_{idx}"
        res_list.append(dic)
    res = {"structure_json_result": res_list}
    return res
