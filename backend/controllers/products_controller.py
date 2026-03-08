from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from backend.auth import verify_token
from backend.utils.embeddings import get_embedding
from configuration.settings import SUPABASE_URL, SUPABASE_KEY

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("/search")
async def search_products(q: str, user_id: str = Depends(verify_token)):
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Generar embedding del texto de búsqueda
        query_embedding = get_embedding(q)
        if not query_embedding:
            raise HTTPException(status_code=500, detail="Error generating embedding")
            
        # Buscar productos similares usando RPC match_products
        # Asumiendo que existe una función RPC match_products o similar
        # Si no existe, usamos ilike como fallback inicial o un error controlado
        try:
             response = supabase.rpc("match_products_by_user", {
                "query_embedding": query_embedding,
                "user_uuid_filter": user_id,
                "match_count": 5
            }).execute()
        except Exception as rpc_error:
             logger.warning(f"RPC match_products failed or not found: {rpc_error}. Falling back to ilike.")
             response = supabase.table("products")\
                .select("*")\
                .ilike("nombre", f"%{q}%")\
                .limit(5)\
                .execute()

        return {"data": response.data}

    except Exception as e:
        logger.error(f"Error in search_products: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching products: {str(e)}")
