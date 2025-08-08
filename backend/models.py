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
class DailyActivity(BaseModel):
    uuid: Optional[str] = None
    client_id: Optional[int] = Field(None, description="ID del usuario (bigint) - se obtiene del token")
    peso: float = Field(default=0, description="Peso en kg (numeric(5,2))")
    grasa: Optional[float] = Field(default=0, description="Porcentaje de grasa corporal (numeric(5,2))")
    musculo: Optional[float] = Field(default=0, description="Masa muscular en kg (numeric(5,2))")
    hambre: int = Field(default=0, description="Nivel de hambre (integer, 0-5)")
    ejercicio: int = Field(default=0, description="Nivel de ejercicio (integer, 0-5)")
    created_at: Optional[date] = Field(default_factory=date.today, description="Fecha de la actividad")

class NutricionalPlan(BaseModel):
    uuid: Optional[str] = None
    client_id: Optional[int] = Field(None, description="ID de telegram (bigint) - se obtiene de la tabla clients")
    created_at: Optional[date] = Field(default_factory=date.today, description="Fecha de creación del plan")
    last_modified_at: Optional[date] = Field(default_factory=date.today, description="Fecha de última modificación del plan")
    daily_kcal: int = Field(default=0, description="Calorías diarias (integer)")
    daily_proteine: int = Field(default=0, description="Proteínas diarias (integer)")
    daily_carbohydrates: int = Field(default=0, description="Carbohidratos diarias (integer)")
    status: PlanStatus = Field(default=PlanStatus.ACTIVE, description="Estado del plan (active, inactive)")
