from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

class PlanStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

# Modelos de autenticación
class UserLogin(BaseModel):
    email: str = Field(..., description="Email del usuario")
    password: str = Field(..., description="Contraseña del usuario")

class UserRegister(BaseModel):
    email: str = Field(..., description="Email del usuario")
    password: str = Field(..., description="Contraseña del usuario")
    name: Optional[str] = Field(None, description="Nombre del usuario")
    telegram_id: int = Field(..., description="ID de Telegram del usuario")

class Token(BaseModel):
    access_token: str
    token_type: str

# Modelo para la tabla daily_activity
class BodyDimensions(BaseModel):
    uuid: Optional[str] = None
    user_uuid: str = Field(None, description="uuid del user, se obtiene del token")
    peso: float = Field(default=0, description="Peso en kg (numeric(5,2))")
    grasa: Optional[float] = Field(default=0, description="Porcentaje de grasa corporal (numeric(5,2))")
    musculo: Optional[float] = Field(default=0, description="Masa muscular en kg (numeric(5,2))")
    cintura: float = Field(default=0, description="circunferencia de cintura en cm (numeric(5,2))")
    created_at: Optional[date] = Field(default_factory=date.today, description="Fecha de la actividad")

class NutricionalPlan(BaseModel):
    uuid: Optional[str] = None
    client_id: Optional[int] = Field(None, description="ID de telegram (bigint) - se obtiene de la tabla clients")
    created_at: Optional[date] = Field(default_factory=date.today, description="Fecha de creación del plan")
    last_modified_at: Optional[date] = Field(default_factory=date.today, description="Fecha de última modificación del plan")
    daily_kcal: int = Field(default=0, description="Calorías diarias (integer)")
    daily_proteine: int = Field(default=0, description="Proteínas diarias (integer)")
    daily_carbohydrates: int = Field(default=0, description="Carbohidratos diarias (integer)")
    daily_fiber: int = Field(default=0, description="Fibra diaria (integer)")
    status: PlanStatus = Field(default=PlanStatus.ACTIVE, description="Estado del plan (active, inactive)")

class MealModel(BaseModel):
    client_id: Optional[int] = Field(None, description="ID de telegram (bigint)")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="Fecha de creación")
    descripcion: str = Field(default='model_default', description="Descripción de la comida")
    peso_total_gr: float = Field(default=0, description="Peso total en gramos")
    energia_kcal: float = Field(default=0, description="Energía total en kcal")
    proteina_gr: float = Field(default=0, description="Proteína total en gramos")
    grasas_gr: float = Field(default=0, description="Grasas totales en gramos")
    carbohidratos_gr: float = Field(default=0, description="Carbohidratos totales en gramos")
    fibra_gr: float = Field(default=0, description="Fibra total en gramos")
    plan_uuid: Optional[str] = Field(default='model_default', description="UUID del plan nutricional")
    product_ids: List[int] = Field(default=[], description="Lista de IDs de productos")
    user_uuid: Optional[str] = Field(None, description="UUID del usuario")  
