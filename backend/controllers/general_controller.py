from fastapi import APIRouter
from configuration.settings import API_BASE_URL, APP_NAME, APP_VERSION

router = APIRouter(prefix="/api", tags=["General"])


# Ruta de prueba para API
@router.get("")
async def root_api():
    return {"message": "Dietik App API is running"}


# Endpoint de prueba sin autenticación
@router.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint working", "status": "success"}


# Endpoint para obtener configuración del frontend
@router.get("/config")
async def get_frontend_config():
    """Endpoint para obtener configuración del frontend"""
    return {
        "api_base_url": API_BASE_URL,
        "app_name": APP_NAME,
        "app_version": APP_VERSION
    }
