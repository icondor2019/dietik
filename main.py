from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from loguru import logger
import sys
import os
from datetime import datetime, timedelta, timezone

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
    API_BASE_URL,
    FRONTEND_URL
)

# Importar módulos locales
from backend.auth import create_access_token, verify_token, authenticate_user, register_user, get_current_user
from backend.models import UserLogin, Token, UserRegister, BodyDimensions, NutricionalPlan
from backend.responses.dashboard_response import DashboardResponse
# from database import db

app = FastAPI(title=APP_NAME, version=APP_VERSION)

# Ruta de prueba para API
@app.get("/api")
async def root_api():
    return {"message": "Dietik App API is running"}

# # Montar archivos estáticos del frontend después de las rutas de la API
# @app.get("/")
# async def read_root():
#     return FileResponse("frontend/login.html")

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
        user = await register_user(user_credentials.email, user_credentials.password,
                                   user_credentials.telegram_id, user_credentials.name)

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
@app.post("/api/create/body-dimensions")
async def create_body_dimensions(activity: BodyDimensions, user_id: str = Depends(verify_token)):
    logger.info(f"Creating body dimension for user {user_id}, activity: {activity}")
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Preparar datos para insertar
        data = {
            "user_uuid": user_id,
            "peso": activity.peso,
            "grasa": activity.grasa or 0,  # Usar 0 si es None
            "musculo": activity.musculo or 0,  # Usar 0 si es None
            "cintura": activity.cintura or 0,  # Usar 0 si es None
        }

        # Si se proporciona una fecha específica, agregarla
        bogota_tz = timezone(timedelta(hours=-5))
        logger.info(f"Activity created_at: {activity.created_at}")
        logger.info(f"Current time in Bogotá: {datetime.now(bogota_tz).isoformat()}")

        if activity.created_at:
            # Si no tiene zona horaria, asumimos que viene en UTC
            if isinstance(activity.created_at, datetime):
                activity_datetime = activity.created_at
            else:
                # Si es date, convertirlo a datetime al inicio del día
                activity_datetime = datetime.combine(activity.created_at, datetime.min.time())

            # Manejar zona horaria
            if activity_datetime.tzinfo is None:
                activity_utc = activity_datetime.replace(tzinfo=timezone.utc)
            else:
                activity_utc = activity_datetime

            bogota_time = activity_utc.astimezone(bogota_tz)
            data["created_at"] = bogota_time.date().isoformat()

        # Insertar en la tabla daily_activity
        response = supabase.table("body_dimensions").insert(data).execute()

        if response.data:
            return {"message": "Daily activity recorded successfully", "data": response.data[0]}
        else:
            raise HTTPException(status_code=400, detail="Failed to record activity")
            
    except Exception as e:
        logger.error(f"Error creating body dimension: {str(e)}")
        logger.exception("Error creating body dimension")
        raise HTTPException(status_code=500, detail=f"Error recording activity: {str(e)}")

@app.get("/api/body-dimensions")
async def get_body_mensions(user_id: str = Depends(verify_token)):
    logger.info(f"[GET] body dimension records for user {user_id}")
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        response = supabase.table("body_dimensions")\
            .select("*")\
            .eq("user_uuid", user_id)\
            .order("created_at", desc=True)\
            .limit(10)\
            .execute()
        # logger.debug(response.data)
        return {"data": response.data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching activity: {str(e)}")

@app.delete("/api/delete/body-dimensions/{dimension_id}")
async def delete_dimension(dimension_id: str, user_id: str = Depends(verify_token)):
    logger.info(f"Deleting body dimension {dimension_id} for user {user_id}")
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Verificar que la comida pertenezca al usuario antes de eliminarla
        record_response = supabase.table("body_dimensions")\
            .select("user_uuid")\
            .eq("uuid", dimension_id)\
            .single()\
            .execute()

        logger.debug(record_response.data)
        if not record_response.data:
            raise HTTPException(status_code=404, detail="dimension not found")
            
        if record_response.data["user_uuid"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this meal")
        
        # Eliminar la comida
        response = supabase.table("body_dimensions")\
            .delete()\
            .eq("uuid", dimension_id)\
            .execute()
        
        logger.info(f"Deleted body dimension {dimension_id}.response: {response}")
        
        return {"message": "Dimension deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting meal: {str(e)}")

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

# Endpoints para control de registros de comidas
@app.get("/api/meals")
async def get_meals(user_id: str = Depends(verify_token)):
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Obtener telegram_id de la tabla clients
        client_response = supabase.table("clients")\
            .select("telegram_id")\
            .eq("supabase_user_uuid", user_id)\
            .execute()
        
        if not client_response.data:
            raise HTTPException(status_code=404, detail="Client not found in clients table")
        
        telegram_id = client_response.data[0]["telegram_id"]
        
        # Obtener los últimos 15 registros de comidas
        try:
            logger.info("Intentando obtener registros de comidas")
            response = supabase.table("meals")\
                .select("uuid, created_at, descripcion, energia_kcal, proteina_gr, carbohidratos_gr")\
                .eq("client_id", telegram_id)\
                .order("created_at", desc=True)\
                .limit(15)\
                .execute()
            
            return {"data": response.data}
            
        except Exception as e:
            logger.error(f"Error específico al obtener meals: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching meals: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error general en get_meals: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in get_meals: {str(e)}")

@app.delete("/api/meals/{meal_id}")
async def delete_meal(meal_id: str, user_id: str = Depends(verify_token)):
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Obtener telegram_id de la tabla clients
        client_response = supabase.table("clients")\
            .select("telegram_id")\
            .eq("supabase_user_uuid", user_id)\
            .execute()
        
        if not client_response.data:
            raise HTTPException(status_code=404, detail="Client not found in clients table")
        
        telegram_id = client_response.data[0]["telegram_id"]
        
        # Verificar que la comida pertenezca al usuario antes de eliminarla
        meal_response = supabase.table("meals")\
            .select("client_id")\
            .eq("uuid", meal_id)\
            .single()\
            .execute()
            
        if not meal_response.data:
            raise HTTPException(status_code=404, detail="Meal not found")
            
        if meal_response.data["client_id"] != telegram_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this meal")
        
        # Eliminar la comida
        response = supabase.table("meals")\
            .delete()\
            .eq("uuid", meal_id)\
            .execute()
        
        return {"message": "Meal deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting meal: {str(e)}")

# Endpoints para planes nutricionales
@app.post("/api/new-nutritional-plan")
async def create_nutritional_plan(plan: NutricionalPlan, user_id: str = Depends(verify_token)):
    logger.info(f"Creating nutritional plan for user {user_id}")
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Obtener telegram_id de la tabla clients
        client_response = supabase.table("clients")\
            .select("telegram_id")\
            .eq("supabase_user_uuid", user_id)\
            .execute()
        
        if not client_response.data:
            raise HTTPException(status_code=404, detail="Client not found in clients table")
        
        telegram_id = client_response.data[0]["telegram_id"]
        
        # Preparar datos para insertar
        data = {
            "client_id": telegram_id,
            "daily_kcal": plan.daily_kcal,
            "daily_proteine": plan.daily_proteine,
            "daily_carbohydrates": plan.daily_carbohydrates,
            "daily_fiber": plan.daily_fiber,
            "status": plan.status
        }
        
        # Si el nuevo plan es activo, desactivar todos los planes activos existentes
        if plan.status == "active":
            update_response = supabase.table("plans")\
                .update({"status": "inactive"})\
                .eq("client_id", telegram_id)\
                .eq("status", "active")\
                .execute()
            
            logger.info(f"Updated {len(update_response.data) if update_response.data else 0} active plans to inactive")

        # Insertar el nuevo plan
        response = supabase.table("plans").insert(data).execute()
        
        if response.data:
            return {"message": "Nutritional plan created successfully", "data": response.data[0]}
        else:
            raise HTTPException(status_code=400, detail="Failed to create plan")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating plan: {str(e)}")

@app.get("/api/nutritional-plans")
async def get_nutritional_plans(user_id: str = Depends(verify_token)):
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Obtener telegram_id de la tabla clients
        client_response = supabase.table("clients")\
            .select("telegram_id")\
            .eq("supabase_user_uuid", user_id)\
            .execute()
        
        if not client_response.data:
            raise HTTPException(status_code=404, detail="Client not found in clients table")
        
        telegram_id = client_response.data[0]["telegram_id"]
        
        # Obtener planes nutricionales del usuario
        response = supabase.table("plans")\
            .select("*")\
            .eq("client_id", telegram_id)\
            .order("created_at", desc=True)\
            .execute()
        
        return {"data": response.data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching plans: {str(e)}")

@app.get("/api/dashboard")
async def get_nutritional_activity(user_id: str = Depends(verify_token)):
    # Obtener la hora actual en Bogotá
    logger.info(f"Generating dashboard for user {user_id}")
    bogota_tz = timezone(timedelta(hours=-5))
    bogota_now = datetime.now(bogota_tz)
    today = bogota_now.date()
    logger.info(f"Current time in Bogotá: {bogota_now.isoformat()} (today: {today})")
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Obtener telegram_id de la tabla clients
        client_response = supabase.table("clients")\
            .select("telegram_id")\
            .eq("supabase_user_uuid", user_id)\
            .execute()

        if not client_response.data:
            raise HTTPException(status_code=404, detail="Client not found in clients table")
        
        telegram_id = client_response.data[0]["telegram_id"]
        
        # Obtener planes nutricionales del usuario
        plan_response = supabase.table("plans")\
            .select("daily_kcal, daily_proteine, daily_fiber")\
            .eq("client_id", telegram_id)\
            .eq("status", "active")\
            .limit(1)\
            .execute()

        # Obtener registros de alimentos de la semana
        meals_response = supabase.table("meals")\
            .select("created_at, energia_kcal, proteina_gr, carbohidratos_gr, fibra_gr")\
            .eq("client_id", telegram_id)\
            .gte("created_at", (datetime.now() - timedelta(weeks=1)).isoformat())\
            .execute()
        logger.info(f"Meals response: {len(meals_response.data)} records found")

        dashboard_response = DashboardResponse()
        if len(plan_response.data) == 0:
            logger.warning(f"No meal records found for user {user_id}")
            return dashboard_response.model_dump()

        meals_today = [
            m for m in meals_response.data
            if datetime.fromisoformat(m["created_at"]).date() == today
            ]
        plan_kcal = plan_response.data[0]["daily_kcal"]
        plan_proteine = plan_response.data[0]["daily_proteine"]
        plan_fiber = plan_response.data[0]["daily_fiber"]

        today_kcal = sum(m.get("energia_kcal", 0) or 0 for m in meals_today)
        today_prot = sum(m.get("proteina_gr", 0) or 0 for m in meals_today)
        today_carb = sum(m.get("carbohidratos_gr", 0) or 0 for m in meals_today)
        today_fiber = sum(m.get("fibra_gr", 0) or 0 for m in meals_today)

        today_kcal_pct = (today_kcal / plan_kcal * 100) if plan_kcal > 0 else 0
        today_prot_pct = (today_prot / plan_proteine * 100) if plan_proteine > 0 else 0
        today_fiber_pct = (today_fiber / plan_fiber * 100) if plan_fiber > 0 else 0

        today_kcal_left = plan_kcal - today_kcal
        today_prot_left = plan_proteine - today_prot
        today_fiber_left = round(plan_fiber - today_fiber)

        today_meal_count = len(meals_today)

        dashboard_response.plan_kcal = plan_kcal
        dashboard_response.plan_proteine = plan_proteine
        dashboard_response.plan_fiber = plan_fiber
        dashboard_response.today_kcal = round(today_kcal)
        dashboard_response.today_proteine = round(today_prot)
        dashboard_response.today_carbohidratos = round(today_carb)
        dashboard_response.today_fiber = round(today_fiber)
        dashboard_response.today_kcal_pct = round(today_kcal_pct)
        dashboard_response.today_prot_pct = round(today_prot_pct)
        dashboard_response.today_fiber_pct = round(today_fiber_pct)
        dashboard_response.meals_count = len(meals_today)
        dashboard_response.today_kcal_left = round(today_kcal_left)
        dashboard_response.today_prot_left = round(today_prot_left)
        dashboard_response.today_fiber_left = round(today_fiber_left)
        dashboard_response.today_meal_count = round(today_meal_count)
        dashboard_response.today_date = today  # Asumiendo que "today" es datetime
        logger.info(f"Dashboard response: {dashboard_response}")

        return dashboard_response.model_dump()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching plans: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT) 