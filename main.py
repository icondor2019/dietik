from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from loguru import logger
import sys
import os

# Importar configuración
from configuration.settings import (
    APP_NAME,
    APP_VERSION,
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS,
    SUPABASE_URL,
    SUPABASE_KEY,
    HOST,
    PORT,
    API_BASE_URL
)

# Importar módulos locales
from backend.auth import create_access_token, verify_token, authenticate_user, register_user, get_current_user
from backend.models import UserLogin, Token, UserRegister, DailyActivity
# from database import db

app = FastAPI(title=APP_NAME, version=APP_VERSION)

# Configuración CORS para permitir requests del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

# Rutas de autenticación
@app.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    try:
        # Autenticar con Supabase
        user = await authenticate_user(user_credentials.email, user_credentials.password)
        
        if user:
            # Crear JWT token
            access_token = create_access_token(
                data={"sub": user.id, "email": user.email}
            )
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

@app.post("/auth/register")
async def register(user_credentials: UserRegister):
    try:
        # Registrar usuario en Supabase
        user = await register_user(user_credentials.email, user_credentials.password)
        
        if user:
            return {"message": "User registered successfully", "user_id": user.id}
        else:
            raise HTTPException(status_code=400, detail="Registration failed")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail="Registration failed")

# Ruta protegida de ejemplo
@app.get("/api/user/profile")
async def get_user_profile(user_id: str = Depends(verify_token)):
    try:
        logger.info(f"Getting user profile for user_id: {user_id}")
        
        # Para obtener datos del usuario, necesitamos el token de Supabase
        # Por ahora, devolvemos la información básica que tenemos del token JWT
        # En una implementación completa, necesitarías almacenar el token de Supabase
        
        return {
            "user_id": user_id,
            "message": "User profile retrieved successfully",
            "note": "Full user data requires Supabase token storage"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Endpoint para daily_activity
@app.post("/api/daily-activity")
async def create_daily_activity(activity: DailyActivity, user_id: str = Depends(verify_token)):
    logger.info(f"Creating daily activity for user {user_id}, activity: {activity}")
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Primero consultar la tabla clients para obtener el telegram_id
        client_response = supabase.table("clients")\
            .select("telegram_id")\
            .eq("supabase_user_uuid", user_id)\
            .execute()
        
        if not client_response.data:
            raise HTTPException(status_code=404, detail="Client not found in clients table")
        
        telegram_id = client_response.data[0]["telegram_id"]
        
        # Preparar datos para insertar
        data = {
            "client_id": telegram_id,  # Usar el telegram_id obtenido de la tabla clients
            "peso": activity.peso,
            "grasa": activity.grasa or 0,  # Usar 0 si es None
            "musculo": activity.musculo or 0,  # Usar 0 si es None
            "hambre": activity.hambre,
            "ejercicio": activity.ejercicio
        }
        
        # Si se proporciona una fecha específica, agregarla
        if activity.created_at:
            data["created_at"] = activity.created_at.isoformat()
        
        # Insertar en la tabla daily_activity
        response = supabase.table("daily_activity").insert(data).execute()
        
        if response.data:
            return {"message": "Daily activity recorded successfully", "data": response.data[0]}
        else:
            raise HTTPException(status_code=400, detail="Failed to record activity")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording activity: {str(e)}")

@app.get("/api/daily-activity")
async def get_daily_activity(user_id: str = Depends(verify_token)):
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Primero consultar la tabla clients para obtener el telegram_id
        client_response = supabase.table("clients")\
            .select("telegram_id")\
            .eq("supabase_user_uuid", user_id)\
            .execute()
        
        if not client_response.data:
            raise HTTPException(status_code=404, detail="Client not found in clients table")
        
        telegram_id = client_response.data[0]["telegram_id"]
        
        # Obtener registros del usuario usando el telegram_id como client_id
        response = supabase.table("daily_activity")\
            .select("*")\
            .eq("client_id", telegram_id)\
            .order("created_at", desc=True)\
            .limit(10)\
            .execute()
        
        return {"data": response.data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching activity: {str(e)}")

# Ruta de prueba
@app.get("/")
async def root():
    return {"message": "Dietik App API is running"}

# Endpoint de prueba sin autenticación
@app.get("/api/test")
async def test_endpoint():
    return {"message": "Test endpoint working", "status": "success"}

# Endpoint para obtener configuración del frontend
@app.get("/api/config")
async def get_frontend_config():
    """Endpoint para obtener configuración del frontend"""
    return {
        "api_base_url": API_BASE_URL,
        "app_name": APP_NAME,
        "app_version": APP_VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT) 