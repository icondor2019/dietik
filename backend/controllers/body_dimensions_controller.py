from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from backend.auth import verify_token
from backend.models import BodyDimensions
from configuration.settings import SUPABASE_URL, SUPABASE_KEY

router = APIRouter(prefix="/api", tags=["Body Dimensions"])


# Endpoint para daily_activity
@router.post("/create/body-dimensions")
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
            "created_at": activity.created_at.isoformat()  # Usar ahora si no se proporciona
        }

        response = supabase.table("body_dimensions").insert(data).execute()

        if response.data:
            return {"message": "Daily activity recorded successfully", "data": response.data[0]}
        else:
            raise HTTPException(status_code=400, detail="Failed to record activity")
            
    except Exception as e:
        logger.error(f"Error creating body dimension: {str(e)}")
        logger.exception("Error creating body dimension")
        raise HTTPException(status_code=500, detail=f"Error recording activity: {str(e)}")


@router.get("/body-dimensions")
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


@router.delete("/delete/body-dimensions/{dimension_id}")
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
