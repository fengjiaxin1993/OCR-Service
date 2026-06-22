from pathlib import Path
from ocr_service.pydantic_settings_file import *


SERVICE_ROOT = Path(".").resolve()


class BasicSettings(BaseFileSettings):
    model_config = SettingsConfigDict(
        yaml_file=str(SERVICE_ROOT / "basic_settings.yaml"),
    )

    # @computed_field
    @cached_property
    def PACKAGE_ROOT(self) -> Path:
        """代码根目录"""
        return Path(__file__).parent

    @cached_property
    def MODEL_PATH(self) -> Path:
        """用户数据根目录"""
        p = SERVICE_ROOT / "models"
        return p


    MAX_OCR_CONCURRENT_NUM: int = 2
    """OCR 最多并行两个"""

    PDF_DPI: int = 200
    """OCR 使用的 DPI（控制 OCR 精度和速度），值越大越耗内存/显存，如遇到 OOM 错误请降低此值"""

    RAPID_DOC_DET_MODEL_PATH :str = str(SERVICE_ROOT / "models/rapid_doc/ch_PP-OCRv5_mobile_det.onnx")
    """rapid_doc 检测模型路径"""

    RAPID_DOC_REC_MODEL_PATH :str = str(SERVICE_ROOT / "models/rapid_doc/ch_PP-OCRv4_rec_mobile.onnx")
    """rapid_doc 识别模型路径"""

    RAPID_DOC_CLS_MODEL_PATH: str = str(SERVICE_ROOT / "models/rapid_doc/ch_ppocr_mobile_v2.0_cls_mobile.onnx")
    """rapid_doc 识别模型路径"""

    RAPID_DOC_LAYOUT_MODEL_PATH  :str = str(SERVICE_ROOT / "models/rapid_doc/pp_doclayoutv2.onnx")
    """布局模型路径"""

    RAPID_DOC_PADDLE_CLS_MODEL_PATH  :str = str(SERVICE_ROOT / "models/rapid_doc/paddle_cls.onnx")
    """表格识别路径"""

    RAPID_DOC_UNET_MODEL_PATH  :str = str(SERVICE_ROOT / "models/rapid_doc/unet.onnx")
    """表格识别路径"""

    RAPID_DOC_SLANET_MODEL_PATH :str = str(SERVICE_ROOT / "models/rapid_doc/slanet-plus.onnx")
    """表格识别路径"""

    DEFAULT_BIND_HOST: str = "127.0.0.1"

    API_SERVER: dict = {"host": DEFAULT_BIND_HOST, "port": 7840}
    """API 服务器地址"""

    def make_dirs(self):
        '''创建所有数据目录'''
        for p in [
            self.MODEL_PATH
        ]:
            p.mkdir(parents=True, exist_ok=True)

    def check_models(self) -> bool:
        """检查模型文件是否存在，不存在则打印提示"""
        required_models = [
            ("RAPID_DOC_DET_MODEL_PATH", self.RAPID_DOC_DET_MODEL_PATH),
            ("RAPID_DOC_REC_MODEL_PATH", self.RAPID_DOC_REC_MODEL_PATH),
            ("RAPID_DOC_CLS_MODEL_PATH", self.RAPID_DOC_CLS_MODEL_PATH),
            ("RAPID_DOC_LAYOUT_MODEL_PATH", self.RAPID_DOC_LAYOUT_MODEL_PATH),
            ("RAPID_DOC_PADDLE_CLS_MODEL_PATH", self.RAPID_DOC_PADDLE_CLS_MODEL_PATH),
            ("RAPID_DOC_UNET_MODEL_PATH", self.RAPID_DOC_UNET_MODEL_PATH),
            ("RAPID_DOC_SLANET_MODEL_PATH", self.RAPID_DOC_SLANET_MODEL_PATH),
        ]

        missing = []
        for name, path in required_models:
            if not Path(path).exists():
                missing.append((name, path))

        if missing:
            print("=" * 60)
            print("⚠️  警告：以下模型文件缺失：")
            for name, path in missing:
                print(f"   - {path}")
            print()
            print("📦 请手动下载模型文件并放置到对应目录：")
            print(f"   {self.PACKAGE_ROOT / 'models' / 'rapid_doc'}")
            print()
            print("=" * 60)
            return False
        return True



class SettingsContainer:
    SERVICE_ROOT = SERVICE_ROOT

    basic_settings: BasicSettings = settings_property(BasicSettings())

    def create_all_templates(self):
        self.basic_settings.create_template_file(write_file=True)

    def set_auto_reload(self, flag: bool = True):
        self.basic_settings.auto_reload = flag


Settings = SettingsContainer()

if __name__ == "__main__":
    Settings.create_all_templates()
