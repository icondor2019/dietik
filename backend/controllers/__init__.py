from fastapi import APIRouter
from backend.controllers.authentication_controller import router as authentication_router
from backend.controllers.user_controller import router as user_router
from backend.controllers.body_dimensions_controller import router as body_dimensions_router
from backend.controllers.meals_controller import router as meals_router
from backend.controllers.products_controller import router as products_router
from backend.controllers.dashboard_controller import router as dashboard_router
from backend.controllers.plans_controller import router as plans_router
from backend.controllers.general_controller import router as general_router
from backend.controllers.health_controller import router as health_router

api_router = APIRouter()

api_router.include_router(authentication_router)
api_router.include_router(user_router)
api_router.include_router(body_dimensions_router)
api_router.include_router(meals_router)
api_router.include_router(products_router)
api_router.include_router(dashboard_router)
api_router.include_router(plans_router)
api_router.include_router(general_router)
api_router.include_router(health_router)
