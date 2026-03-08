from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from backend.auth import verify_token
from backend.models import NutricionalPlan
from configuration.settings import SUPABASE_URL, SUPABASE_KEY

router = APIRouter(prefix="/api", tags=["Nutritional Plans"])


# Endpoints para planes nutricionales
@router.post("/new-nutritional-plan")
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
            "status": plan.status,
            "user_uuid": user_id
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


@router.get("/nutritional-plans")
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
