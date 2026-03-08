from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from loguru import logger
import os
from contextlib import asynccontextmanager

# Importar configuración
from configuration.settings import (
    APP_NAME,
    APP_VERSION,
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS,
    HOST,
    PORT,
)

# Importar controladores
from backend.controllers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Dietik App...")
    yield
    logger.info("Closing Dietik App...")


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Configuración CORS para permitir requests del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)


@app.middleware("http")
async def serve_spa(request: Request, call_next):
    response = await call_next(request)
    
    # Solo servir HTML si la ruta no es API ni un archivo estático
    if response.status_code == 404 and not request.url.path.startswith("/api") and not os.path.splitext(request.url.path)[1]:
        return FileResponse("frontend/login.html")
    return response


def setup_application():
    app.include_router(api_router)


setup_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)