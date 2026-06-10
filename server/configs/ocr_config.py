# configs/offline_config.py

# ==================== OCR 模型本地路径配置 ====================
import os
from server.configs.basic_config import MODEL_DIR

# paddle_ocr信息
PADDLE_OCR_MODEL = os.path.join(MODEL_DIR, "paddle_ocr")

# 检测模型
PADDLE_DET_MODEL_NAME = "PP-OCRv5_mobile_det"
# 检测模型路径
PADDLE_DET_MODEL_PATH = os.path.join(PADDLE_OCR_MODEL, PADDLE_DET_MODEL_NAME)

# 识别模型
PADDLE_REC_MODEL_NAME = "PP-OCRv5_mobile_rec"
# 识别模型路径
PADDLE_REC_MODEL_PATH = os.path.join(PADDLE_OCR_MODEL, PADDLE_REC_MODEL_NAME)

# rapid_doc信息
RAPID_DOC_OCR_MODEL = os.path.join(MODEL_DIR, "rapid_doc")

RAPID_DOC_DET_MODEL_PATH = os.path.join(RAPID_DOC_OCR_MODEL, "ch_PP-OCRv5_mobile_det.onnx")
RAPID_DOC_REC_MODEL_PATH = os.path.join(RAPID_DOC_OCR_MODEL, "ch_PP-OCRv5_rec_mobile_infer.onnx")
RAPID_DOC_LAYOUT_MODEL_PATH = os.path.join(RAPID_DOC_OCR_MODEL, "pp_doclayoutv2.onnx")
RAPID_DOC_UNET_MODEL_PATH = os.path.join(RAPID_DOC_OCR_MODEL, "unet.onnx")
RAPID_DOC_SLANET_MODEL_PATH = os.path.join(RAPID_DOC_OCR_MODEL, "slanet-plus.onnx")
