# OCR-Service

基于 **RapidOCR** 的高性能 PDF OCR 识别与文档结构化解析服务，提供 RESTful API 接口，支持 PDF 文档的文字识别、版面分析、表格提取与 Markdown 格式输出。

## 目录

- [项目结构](#项目结构)
- [技术栈](#技术栈)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
  - [1. 安装依赖](#1-安装依赖)
  - [2. 准备模型文件](#2-准备模型文件)
  - [3. 启动服务](#3-启动服务)
- [API 接口文档](#api-接口文档)
  - [1. 健康检查](#1-健康检查)
  - [2. PDF 解析提取信息](#2-pdf-解析提取信息)
- [命令行参数](#命令行参数)
- [配置说明](#配置说明)
- [核心流程](#核心流程)

---

## 项目结构

```
OCR-Service/
├── app.py                           # 应用入口，服务启动
├── requirements.txt                 # Python 依赖
├── readme.md                        # 项目说明文档
├── models/                          # ONNX 模型文件目录
│   ├── ch_PP-OCRv5_mobile_det.onnx  # 文字检测模型
│   ├── ch_PP-OCRv5_rec_mobile_infer.onnx  # 文字识别模型
│   ├── pp_doclayoutv2.onnx          # 版面分析模型
│   ├── unet.onnx                    # U-Net 表格检测模型
│   ├── slanet-plus.onnx             # SLANet+ 表格结构识别模型
│   └── ...
└── server/                          # 服务核心代码
    ├── api_server/
    │   ├── server_app.py            # FastAPI 应用创建与配置
    │   └── main_routes.py           # API 路由定义
    ├── configs/
    │   ├── basic_config.py          # 基础路径配置
    │   └── ocr_config.py            # OCR 模型路径配置
    └── ocr/
        ├── ocr_service.py           # OCR 业务逻辑（健康检查、PDF解析）
        ├── ocr_helper.py            # 工具函数（PDF转图片、表格转换）
        ├── ocr_extract_utils.py     # OCR 结果提取与结构化
        └── single_ocr_engine.py     # RapidDoc 引擎单例管理
```

---

## 技术栈

| 类别 | 技术 |
|------|------|
| Web 框架 | FastAPI + Uvicorn |
| OCR 引擎 | RapidOCR / RapidDoc |
| 深度学习推理 | ONNX Runtime |
| PDF 处理 | PyMuPDF (fitz) |
| 图像处理 | OpenCV、Pillow、NumPy |
| 表格解析 | SLANet+ + U-Net |
| 文本结构化 | LangChain MarkdownHeaderTextSplitter |
| 并发控制 | asyncio.Semaphore |

---

## 环境要求

- Python >= 3.8
- pip 包管理器

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备模型文件

将以下 ONNX 模型文件放置于 `models/rapid_doc/` 目录下（或通过配置自定义路径）：

| 文件名 | 用途 |
|--------|------|
| `ch_PP-OCRv5_mobile_det.onnx` | 文字检测模型 |
| `ch_PP-OCRv5_rec_mobile_infer.onnx` | 文字识别模型 |
| `pp_doclayoutv2.onnx` | 版面布局分析模型 |
| `unet.onnx` | U-Net 表格区域检测 |
| `slanet-plus.onnx` | SLANet+ 表格结构识别 |

> 模型可从 [RapidOCR 官方仓库](https://github.com/RapidAI/RapidOCR) 获取。

### 3. 启动服务

```bash
# 默认配置启动（监听 127.0.0.1:7840）
python app.py

# 自定义端口和并发数
python app.py --port 8080 --rapid_max_concurrent 5 --dpi 300
```

启动成功后访问：
- API 文档（Swagger UI）：http://127.0.0.1:7840/docs
- 健康检查：http://127.0.0.1:7840/api/health

---

## API 接口文档

### 1. 健康检查

检查服务是否正常运行。

**请求**

```
GET /api/health
```

**响应示例**

```json
{
  "status": "ok",
  "RAPID_DOC_MAX_CONCURRENT": 2,
  "DPI": 200
}
```

**响应参数说明**

| 参数 | 类型 | 说明 |
|------|------|------|
| status | string | 服务状态，`"ok"` 表示正常 |
| RAPID_DOC_MAX_CONCURRENT | integer | 当前最大并发解析数 |
| DPI | integer | 当前 PDF 转图片使用的 DPI |

---

### 2. PDF 解析提取信息

上传 PDF 文件路径，进行 OCR 识别与文档结构化解析，返回 Markdown 文本、版面分析结果和结构化 JSON。

**请求**

```
POST /api/parse/pdf2info
Content-Type: application/json
```

**请求参数（JSON Body）**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file_path | string | 是 | PDF 文件的本地绝对路径 |

**请求示例**

```json
{
  "file_path": "/data/documents/example.pdf"
}
```

**响应示例**

```json
{
  "success": true,
  "processing_time": 2.35,
  "filename": "example.pdf",
  "filepath": "/data/documents/example.pdf",
  "markdown": "# 标题\n\n这是识别出的文本内容...\n\n| 列1 | 列2 |\n|---|---|\n| 值1 | 值2 |",
  "layoutParsingResults": "{\n  \"layout_res_list\": [\n    {\n      \"meta\": {\n        \"page_idx\": 0,\n        \"page_width\": 595,\n        \"page_height\": 842\n      },\n      \"parsing_res_list\": [\n        {\n          \"block_id\": \"block_0_0_0\",\n          \"block_content\": \"识别出的文字\",\n          \"block_type\": \"text\",\n          \"block_bbox\": [10, 20, 200, 50],\n          \"doc_id\": \"doc_0\"\n        }\n      ]\n    }\n  ]\n}",
  "structureJsonResults": "{\n  \"structure_json_result\": [\n    {\n      \"title\": \"标题\",\n      \"text\": \"这是识别出的文本内容...\",\n      \"doc_id\": \"doc_0\"\n    }\n  ]\n}"
}
```

**响应参数说明**

| 参数 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否解析成功，`true` / `false` |
| processing_time | number | 处理耗时（秒） |
| filename | string | PDF 文件名 |
| filepath | string | PDF 文件完整路径 |
| markdown | string | OCR 识别后的 Markdown 格式文本（含表格已转换为标准 Markdown 表格） |
| layoutParsingResults | string (JSON) | 版面分析结果 JSON 字符串，详见下方说明 |
| structureJsonResults | string (JSON) | 文档结构化 JSON 字符串，按标题层级拆分 |
| error | string | 错误信息（仅在 `success` 为 `false` 时返回） |

**layoutParsingResults 解析后结构**

```json
{
  "layout_res_list": [
    {
      "meta": {
        "page_idx": 0,
        "page_width": 595,
        "page_height": 842
      },
      "parsing_res_list": [
        {
          "block_id": "block_{页码}_{段落}_{序号}",
          "block_content": "文字内容",
          "block_type": "text",
          "block_bbox": [x1, y1, x2, y2],
          "doc_id": "doc_0"
        }
      ]
    }
  ]
}
```

| 字段 | 说明 |
|------|------|
| layout_res_list | 按页组织的版面分析结果列表 |
| meta.page_idx | PDF 页码（从 0 开始） |
| meta.page_width | 页面宽度（像素） |
| meta.page_height | 页面高度（像素） |
| parsing_res_list | 当前页的文本块列表 |
| block_id | 文本块唯一标识 |
| block_content | 文本块内容 |
| block_type | 块类型（`text`） |
| block_bbox | 文本块边界框 `[x1, y1, x2, y2]` |
| doc_id | 对应的结构化文档段落 ID |

**structureJsonResults 解析后结构**

```json
{
  "structure_json_result": [
    {
      "title": "章节标题",
      "text": "该章节的完整文本内容",
      "doc_id": "doc_0"
    }
  ]
}
```

| 字段 | 说明 |
|------|------|
| structure_json_result | 按 Markdown 标题层级拆分的段落列表 |
| title | 段落所属的 Markdown 标题（`#` / `##` / `###` / `####`） |
| text | 该标题下的文本内容 |
| doc_id | 段落唯一标识，与 `layoutParsingResults` 中的 `doc_id` 对应 |

**错误响应示例**

```json
{
  "success": false,
  "processing_time": 0.0,
  "filename": "example.pdf",
  "filepath": "/data/documents/example.pdf",
  "markdown": "",
  "layoutParsingResults": "",
  "structureJsonResults": "",
  "error": "文件不存在: /data/documents/example.pdf"
}
```

---

## 命令行参数

启动服务时支持以下命令行参数：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--host` | string | `127.0.0.1` | 服务监听地址 |
| `--port` | int | `7840` | 服务监听端口 |
| `--log_level` | string | `info` | 日志级别（debug/info/warning/error） |
| `--dpi` | int | `200` | PDF 转图片的 DPI（影响 OCR 精度与速度） |
| `--rapid_max_concurrent` | int | `2` | RapidDoc 文档解析最大并发数 |

---

## 配置说明

核心配置通过环境变量或命令行参数控制：

| 环境变量 | 对应命令行参数 | 默认值 | 说明 |
|----------|---------------|--------|------|
| `RAPID_DOC_MAX_CONCURRENT` | `--rapid_max_concurrent` | `2` | 最大并发解析数，建议根据 GPU/CPU 资源调整 |
| `DPI` | `--dpi` | `200` | PDF 渲染 DPI，值越大精度越高但速度越慢 |

模型路径配置位于 `server/configs/ocr_config.py`，默认从 `models/rapid_doc/` 加载模型文件。

---

## 核心流程

```
用户请求 (POST /api/parse/pdf2info)
        │
        ▼
  验证文件路径与格式
        │
        ▼
  PDF → 图片列表 (PyMuPDF + DPI)
        │
        ▼
  RapidDoc 引擎处理 (并发限制信号量)
  ├── 文字检测 (ONNX DET)
  ├── 文字识别 (ONNX REC)
  ├── 版面分析 (PP-DocLayoutV2)
  └── 表格识别 (SLANet+ + U-Net)
        │
        ▼
  结果后处理
  ├── HTML表格 → Markdown表格
  ├── Markdown标题结构化拆分
  └── 版面信息提取 (bbox/doc_id)
        │
        ▼
  返回 JSON 响应
  ├── markdown
  ├── layoutParsingResults
  └── structureJsonResults
```
