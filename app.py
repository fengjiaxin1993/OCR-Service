"""
FastAPI 后端主应用 - PDF OCR 与关键词定位系统
前后端分离架构
"""
import argparse
import os

import uvicorn
from server.api_server.server_app import create_app


# -------------- 配置日志（在抑制 stderr 之前设置） --------------


def run_api_server():
    parser = argparse.ArgumentParser(description="启动 RapidDoc 服务")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="监听地址")
    parser.add_argument("--port", type=int, default=7840, help="监听端口")
    parser.add_argument("--log_level", type=str, default="info", help="日志级别")
    parser.add_argument("--dpi", type=int, default=200, help="PDF转图片的DPI")
    parser.add_argument("--rapid_max_concurrent", type=int, default=2, help="RapidDoc文档解析最大并发数")
    args = parser.parse_args()

    # 设置环境变量
    os.environ["RAPID_DOC_MAX_CONCURRENT"] = str(args.rapid_max_concurrent)
    os.environ["DPI"] = str(args.dpi)

    print(f"启动 RapidDoc 服务: http://{args.host}:{args.port}")
    print(f"DPI: {args.dpi}")
    print(f"最大rapidDoc并发数: {args.rapid_max_concurrent}")
    print(f"日志级别: {args.log_level}")
    print(f"API 文档: http://{args.host}:{args.port}/docs")

    app = create_app()
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        reload=False,  # 生产环境关闭 reload
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
        }
    )


if __name__ == "__main__":
    run_api_server()
# python app.py --port 8080 --rapid_max_concurrent 5 --paddle_max_concurrent 3