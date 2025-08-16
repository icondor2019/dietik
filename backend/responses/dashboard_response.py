from pydantic import BaseModel, Field
from datetime import datetime

class DashboardResponse(BaseModel):
    plan_kcal: float = Field(default=0)
    plan_proteine: float = Field(default=0)
    plan_fiber: float = Field(default=0)
    # Consumo de hoy
    today_kcal: float = Field(default=0)
    today_proteine: float = Field(default=0)
    today_carbohidratos: float = Field(default=0)
    today_fiber: float = Field(default=0)
    today_grasa: float = Field(default=0)
    # Porcentajes de cumplimiento
    today_kcal_pct: float = Field(default=0)
    today_prot_pct: float = Field(default=0)
    today_fiber_pct: float = Field(default=0)
    # Lo que queda para cumplir la meta
    today_kcal_left: float = Field(default=0)
    today_prot_left: float = Field(default=0)
    today_fiber_left: float = Field(default=0)
    today_date: datetime = Field(default_factory=datetime.utcnow)
    weekly_kcal: dict = Field(default_factory=dict, description="Calorías diarias de la última semana")

    class Config:
        extra = "forbid"  # Campos adicionales NO permitidos
        allow_mutation = True  # Permitir modificar campos después de crear instancia
