from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from backend.auth import verify_token

router = APIRouter(prefix="/api/user", tags=["User"])


@router.get("/profile")
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
