# Apply pathlib patches before any other imports to fix WindowsPath issues
import uvicorn
import logging
# 屏蔽第三方库的冗余日志
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("rapid_doc").setLevel(logging.WARNING)
logging.getLogger("rapidocr").setLevel(logging.WARNING)
logging.getLogger("rapid_table").setLevel(logging.WARNING)
logging.getLogger("rapid_layout").setLevel(logging.WARNING)
logging.getLogger("onnxruntime").setLevel(logging.WARNING)
import click
from ocr_service.settings import Settings
from ocr_service.server.api_server.server_app import create_app


def run_api_server():
    app = create_app()
    host = Settings.basic_settings.API_SERVER["host"]
    port = Settings.basic_settings.API_SERVER["port"]
    print(f"服务地址:  http://{host}:{port}")
    print(f"API 文档:  http://{host}:{port}/docs")
    print("=" * 50)
    uvicorn.run(app, host=host, port=port)

@click.command(help="启动服务")
def main():
    run_api_server()


if __name__ == "__main__":
    main()
