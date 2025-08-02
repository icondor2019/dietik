from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from models import (
    FoodItem, FoodConsumption, DailyGoals, Exercise, 
    BodyMeasurements, DailySummary, WeeklySummary
)

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )

# Instancia global del manager de base de datos
db = DatabaseManager() 