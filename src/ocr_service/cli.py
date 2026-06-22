import shutil
import warnings
# 屏蔽 pydantic 模块下所有 UserWarning
warnings.filterwarnings("ignore", category=UserWarning, module=r"pydantic.*")
import click
from ocr_service.settings import Settings
from ocr_service.startup import main as startup_main


# 步骤1：创建命令组（所有子命令的容器）
@click.group(help="chatchat 命令行工具")
def main():
    ...


# 步骤2：添加子命令1：init（初始化配置）
@main.command("init", help="项目初始化")
def init():
    bs = Settings.basic_settings
    Settings.set_auto_reload(False)
    if bs.PACKAGE_ROOT / "models" != bs.MODEL_PATH:
        shutil.copytree(bs.PACKAGE_ROOT / "models", bs.MODEL_PATH,
                        dirs_exist_ok=True)
    print("复制 MODELS文件：成功。")
    Settings.create_all_templates()
    Settings.set_auto_reload(True)
    print("生成默认配置文件：成功。")
    # 启动时检查模型
    Settings.basic_settings.check_models()


main.add_command(startup_main, "start")

# 项目入口（调用命令组）
if __name__ == "__main__":
    main()
