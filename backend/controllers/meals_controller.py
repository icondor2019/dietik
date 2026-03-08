from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from backend.auth import verify_token
from backend.models import MealModel
from configuration.settings import SUPABASE_URL, SUPABASE_KEY

router = APIRouter(prefix="/api/meals", tags=["Meals"])


# Endpoints para control de registros de comidas
@router.get("")
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


@router.get("/frequent")
async def get_frequent_meals(user_id: str = Depends(verify_token)):
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Usar RPC get_frequent_products
        response = supabase.rpc("get_frequent_products", {"p_user_uuid": user_id}).execute()
        
        return {"data": response.data}

    except Exception as e:
        logger.error(f"Error in get_frequent_meals: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting frequent meals: {str(e)}")


@router.delete("/delete/{meal_id}")
async def delete_meal(meal_id: str, user_id: str = Depends(verify_token)):
    logger.warning(f"Deleting meal {meal_id} for user {user_id}")
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


@router.post("/create")
async def create_meal(meal: MealModel, user_id: str = Depends(verify_token)):
    logger.info(f"Creating meal for user {user_id}")
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        plan_response = supabase.table("plans")\
            .select("uuid", "client_id")\
            .eq("user_uuid", user_id)\
            .eq("status", "active")\
            .execute()

        if not plan_response.data:
            raise HTTPException(status_code=404, detail="Client not found in clients table")

        telegram_id = plan_response.data[0]["client_id"]

        # Preparar datos para insertar basado en modelo mealModel
        data = {
            "client_id": telegram_id,
            "energia_kcal": meal.energia_kcal,
            "proteina_gr": meal.proteina_gr,
            "carbohidratos_gr": meal.carbohidratos_gr,
            "fibra_gr": meal.fibra_gr,
            "grasas_gr": meal.grasas_gr,
            "user_uuid": user_id,
            "descripcion": meal.descripcion,
            "peso_total_gr": int(meal.peso_total_gr),
            "product_ids": meal.product_ids,
            "plan_uuid": plan_response.data[0]["uuid"]
        }
        logger.info(f"Data: {data}")
        # Insertar datos en la tabla meals
        insert_response = supabase.table("meals")\
            .insert(data)\
            .execute()

        return {"data": insert_response.data}
    except Exception as e:
        logger.error(f"Error creating meal: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating meal: {str(e)}")
