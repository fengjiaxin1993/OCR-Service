from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from ocr_service.server.api_server.main_routes import ocr_router
from ocr_service.server.ocr.ocr_service import startup_event


def create_app():
    app = FastAPI(title="OCR API Server")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", summary="swagger 文档", include_in_schema=False)
    async def document():
        return RedirectResponse(url="/docs")

    @app.on_event("startup")
    async def on_startup():
        """服务启动时执行初始化"""
        await startup_event()

    app.include_router(ocr_router)

    return app
