from fastapi import APIRouter

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("")
async def health_check():
    """Simple endpoint to check if the app is running."""
    return {"status": "healthy", "message": "Dietik App is running"}
