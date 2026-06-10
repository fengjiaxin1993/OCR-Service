# configs/basic_config.py
# 基础配置

import os

# project 根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 模型目录
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# OCR 使用的 DPI（控制 OCR 精度和速度）
PDF_DPI = int(os.environ.get("RAPID_DOC_DPI", "300"))
