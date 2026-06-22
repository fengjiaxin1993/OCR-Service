# OCR-Service

基于 **RapidOCR** 的高性能 PDF OCR 识别与文档结构化解析服务，提供 RESTful API 接口，支持 PDF 文档的文字识别、版面分析、表格提取与 Markdown 格式输出。

> 使用 **Poetry** 构建，通过 **config.yaml** 配置文件管理所有参数，无需修改代码。

## 目录

- [项目结构](#项目结构)
- [技术栈](#技术栈)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
  - [1. 安装 Poetry](#1-安装-poetry)
  - [2. 安装依赖](#2-安装依赖)
  - [3. 准备模型文件](#3-准备模型文件)
  - [4. 配置服务](#4-配置服务)
  - [5. 启动服务](#5-启动服务)
- [API 接口文档](#api-接口文档)
  - [1. 健康检查](#1-健康检查)
  - [2. PDF 解析提取信息](#2-pdf-解析提取信息)
- [配置说明](#配置说明)
  - [配置优先级](#配置优先级)
  - [环境变量覆盖](#环境变量覆盖)
  - [命令行参数](#命令行参数)
- [核心流程](#核心流程)

---

## 项目结构

```
OCR-Service/
├── pyproject.toml              # Poetry 项目配置（依赖、脚本入口）
├── config.yaml                 # 服务配置文件（可自定义修改）
├── app.py                      # 便捷启动入口（python app.py）
├── readme.md                   # 项目说明文档
├── models/                     # ONNX 模型文件目录（由 config.yaml 指定）
│   └── rapid_doc/
│       ├── ch_PP-OCRv5_mobile_det.onnx
│       ├── ch_PP-OCRv4_rec_mobile.onnx
│       ├── ch_ppocr_mobile_v2.0_cls_mobile.onnx
│       ├── pp_doclayoutv2.onnx
│       ├── unet.onnx
│       ├── slanet-plus.onnx
│       ├── paddle_cls.onnx
│       └── ...
└── src/
    └── ocr_service/            # Python 包
        ├── __init__.py
        ├── main.py             # 启动入口函数（Poetry scripts 入口）
        └── server/
            ├── api_server/
            │   ├── server_app.py     # FastAPI 应用创建
            │   └── main_routes.py    # API 路由定义
            ├── configs/
            │   ├── settings.py       # 配置加载器（YAML + 环境变量）
            │   ├── basic_config.py   # 基础配置（从 settings 加载）
            │   └── ocr_config.py     # 模型路径配置（从 settings 加载）
            └── ocr/
                ├── ocr_service.py          # OCR 业务逻辑
                ├── ocr_helper.py           # 工具函数（PDF转图片、表格转换）
                ├── ocr_extract_utils.py    # OCR 结果提取与结构化
                └── single_ocr_engine.py    # RapidDoc 引擎单例管理
```

---

## 技术栈

| 类别 | 技术 |
|------|------|
| 包管理 | Poetry |
| Web 框架 | FastAPI + Uvicorn |
| OCR 引擎 | RapidOCR / RapidDoc |
| 深度学习推理 | ONNX Runtime |
| PDF 处理 | PyMuPDF (fitz) |
| 图像处理 | OpenCV、Pillow、NumPy |
| 表格解析 | SLANet+ + U-Net |
| 文本结构化 | LangChain MarkdownHeaderTextSplitter |
| 配置管理 | PyYAML |

---

## 环境要求

- Python >= 3.8, < 3.12
- Poetry >= 1.7.0

## 快速开始

### 1. 安装 Poetry

```bash
# 推荐使用官方安装器
pip install poetry

# 或使用 pipx
pipx install poetry
```

### 2. 安装依赖

```bash
poetry install
```

### 3. 准备模型文件

将 ONNX 模型文件放置于 `models/rapid_doc/` 目录下（路径可在 `config.yaml` 中自定义）：

| 文件名 | 用途 |
|--------|------|
| `ch_PP-OCRv5_mobile_det.onnx` | 文字检测模型 |
| `ch_PP-OCRv4_rec_mobile.onnx` | 文字识别模型 |
| `ch_ppocr_mobile_v2.0_cls_mobile.onnx` | 文字方向分类模型 |
| `pp_doclayoutv2.onnx` | 版面布局分析模型 |
| `unet.onnx` | U-Net 表格区域检测 |
| `slanet-plus.onnx` | SLANet+ 表格结构识别 |
| `paddle_cls.onnx` | 表格分类模型 |

> 模型可从 [RapidOCR 官方仓库](https://github.com/RapidAI/RapidOCR) 获取。

### 4. 配置服务

编辑 `config.yaml` 文件修改服务参数，无需改动任何代码：

```yaml
server:
  host: "127.0.0.1"
  port: 7840
  log_level: "info"

ocr:
  dpi: 200
  max_concurrent: 2
  batch_size: 1

models:
  base_dir: "models"        # 可改为绝对路径
  rapid_doc_dir: "rapid_doc"
```

详见 [配置说明](#配置说明)。

### 5. 启动服务

```bash
# 方式1: 使用 Poetry 脚本入口（推荐）
poetry run ocr-service

# 方式2: 直接运行 app.py
poetry run python app.py

# 方式3: 指定配置文件或覆盖参数
poetry run ocr-service --config /path/to/config.yaml --port 8080 --dpi 300
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
  "markdown_text": "# 标题\n\n这是识别出的文本内容...",
  "locate_json_result": {
    "layout_res_list": [
      {
        "meta": {
          "page_idx": 0,
          "page_width": 595,
          "page_height": 842
        },
        "parsing_res_list": [
          {
            "block_id": "block_0_0_0",
            "block_content": "识别出的文字",
            "block_type": "text",
            "block_bbox": [10, 20, 200, 50],
            "doc_id": "doc_0"
          }
        ]
      }
    ]
  },
  "structure_json_result": {
    "structure_json_result": [
      {
        "title": "标题",
        "text": "这是识别出的文本内容...",
        "doc_id": "doc_0"
      }
    ]
  },
  "error": ""
}
```

**响应参数说明**

| 参数 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否解析成功 |
| processing_time | number | 处理耗时（秒） |
| markdown_text | string | OCR 识别后的 Markdown 格式文本（含表格已转换为标准 Markdown 表格） |
| locate_json_result | object | 版面分析结果，详见下方说明 |
| structure_json_result | object | 文档结构化结果，按标题层级拆分 |
| error | string | 错误信息（仅在 `success` 为 `false` 时返回） |

**locate_json_result 结构**

| 字段 | 说明 |
|------|------|
| layout_res_list | 按页组织的版面分析结果列表 |
| meta.page_idx | PDF 页码（从 0 开始） |
| meta.page_width / page_height | 页面尺寸（像素） |
| parsing_res_list.block_id | 文本块唯一标识 `block_{页码}_{段落}_{序号}` |
| parsing_res_list.block_content | 文本块内容 |
| parsing_res_list.block_type | 块类型（`text`） |
| parsing_res_list.block_bbox | 边界框 `[x1, y1, x2, y2]` |
| parsing_res_list.doc_id | 对应结构化段落 ID |

**structure_json_result 结构**

| 字段 | 说明 |
|------|------|
| structure_json_result | 按 Markdown 标题层级拆分的段落列表 |
| title | 段落所属标题（`#` ~ `####`） |
| text | 该标题下的文本内容 |
| doc_id | 段落唯一标识，与 `locate_json_result` 中的 `doc_id` 对应 |

**错误响应示例**

```json
{
  "success": false,
  "processing_time": 0.0,
  "markdown_text": "",
  "locate_json_result": {},
  "structure_json_result": {},
  "error": "文件不存在: /data/documents/example.pdf"
}
```

---

## 配置说明

所有配置集中在 `config.yaml` 文件中，修改此文件即可调整服务行为。

### 配置优先级

从低到高：

1. **内置默认值** — `settings.py` 中的 `_DEFAULT_CONFIG`
2. **config.yaml 文件** — 覆盖默认值
3. **环境变量** — 覆盖配置文件（如 `OCR_SERVER_PORT=8080`）
4. **命令行参数** — 覆盖一切（如 `--port 8080`）

### 环境变量覆盖

| 环境变量 | 对应配置项 | 类型 | 示例 |
|----------|-----------|------|------|
| `OCR_CONFIG_PATH` | 配置文件路径 | string | `/etc/ocr/config.yaml` |
| `OCR_SERVER_HOST` | server.host | string | `0.0.0.0` |
| `OCR_SERVER_PORT` | server.port | int | `8080` |
| `OCR_LOG_LEVEL` | server.log_level | string | `debug` |
| `OCR_DPI` | ocr.dpi | int | `300` |
| `OCR_MAX_CONCURRENT` | ocr.max_concurrent | int | `5` |
| `OCR_BATCH_SIZE` | ocr.batch_size | int | `2` |
| `OCR_MODEL_BASE_DIR` | models.base_dir | string | `/data/models` |

### 命令行参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `--host` | string | 监听地址（覆盖配置文件） |
| `--port` | int | 监听端口（覆盖配置文件） |
| `--log_level` | string | 日志级别（覆盖配置文件） |
| `--dpi` | int | PDF转图片DPI（覆盖配置文件） |
| `--max_concurrent` | int | 最大并发数（覆盖配置文件） |
| `--config` | string | 配置文件路径（默认: config.yaml） |

---

## 核心流程

```
用户请求 (POST /api/parse/pdf2info)
        │
        ▼
  加载配置 (config.yaml → settings → env → CLI)
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
  ├── markdown_text
  ├── locate_json_result
  └── structure_json_result
```

---

## 1.开发说明
### 1.1 源码启动

```bash
cd OCR-Service
cd src/ocr_service
python cli.py init
python cli.py start
```

### 1.2 pip可编辑安装（不依赖poetry）启动

```bash
cd OCR-Service
# 可编辑模式安装项目（代码修改实时生效）
pip install -e .
# 安装后同样可以直接使用 CLI 命令：
# 初始化
icdo init
# 启动服务
icdo start
```

## 2.构建wheel包说明(通过poetry)

```bash
cd OCR-Service
poetry build
# 安装包在dist目录下
```

## 3. conda 部署

```bash
conda create -n ICDO-RNV python=3.11
conda activate ICDO-RNV
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
or
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 安装icdo
pip install dist/icdo-1.2.0.tar.gz
```
## 4. 启动项目
```bash
# 初始化
ocr-service init
# 启动服务
ocr-service start
```