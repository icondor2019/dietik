from pydantic import BaseModel, Field
from datetime import datetime

class DashboardResponse(BaseModel):
    plan_kcal: float = Field(default=0)
    plan_proteine: float = Field(default=0)
    plan_fiber: float = Field(default=0)
    today_kcal: float = Field(default=0)
    today_proteine: float = Field(default=0)
    today_carbohidratos: float = Field(default=0)
    today_fiber: float = Field(default=0)
    today_kcal_pct: float = Field(default=0)
    today_prot_pct: float = Field(default=0)
    today_fiber_pct: float = Field(default=0)
    meals_count: int = Field(default=0)
    today_kcal_left: float = Field(default=0)
    today_prot_left: float = Field(default=0)
    today_fiber_left: float = Field(default=0)
    today_meal_count: int = Field(default=0)
    today_date: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        extra = "forbid"  # Campos adicionales NO permitidos
        allow_mutation = True  # Permitir modificar campos después de crear instancia
