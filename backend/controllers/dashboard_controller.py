from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from datetime import datetime, timedelta, timezone
import traceback
from backend.auth import verify_token
from backend.responses.dashboard_response import DashboardResponse
from configuration.settings import SUPABASE_URL, SUPABASE_KEY

router = APIRouter(prefix="/api", tags=["Dashboard"])


@router.get("/dashboard")
async def get_nutritional_activity(user_id: str = Depends(verify_token)):
    # Obtener la hora actual en Bogotá
    logger.info(f"Generating dashboard for user {user_id}")
    bogota_tz = timezone(timedelta(hours=-5))
    bogota_now = datetime.now(bogota_tz)
    today = bogota_now.date()
    logger.info(f"Current time in Bogotá: {bogota_now.isoformat()} (today: {today})")
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Obtener telegram_id de la tabla clients
        client_response = supabase.table("clients")\
            .select("telegram_id")\
            .eq("supabase_user_uuid", user_id)\
            .execute()

        if not client_response.data:
            raise HTTPException(status_code=404, detail="Client not found in clients table")
        
        telegram_id = client_response.data[0]["telegram_id"]
        
        # Obtener planes nutricionales del usuario
        plan_response = supabase.table("plans")\
            .select("daily_kcal, daily_proteine, daily_fiber")\
            .eq("client_id", telegram_id)\
            .eq("status", "active")\
            .limit(1)\
            .execute()

        # Obtener registros de alimentos de la semana
        meals_response = supabase.table("meals")\
            .select("created_at, energia_kcal, proteina_gr, carbohidratos_gr, fibra_gr, grasas_gr")\
            .eq("client_id", telegram_id)\
            .gte("created_at", (datetime.now() - timedelta(weeks=2)).isoformat())\
            .execute()
        logger.info(f"Meals response: {len(meals_response.data)} records found")

        dashboard_response = DashboardResponse()
        if len(plan_response.data) == 0:
            logger.warning(f"No meal records found for user {user_id}")
            return dashboard_response.model_dump()

        meals_today = [
            m for m in meals_response.data
            if datetime.fromisoformat(m["created_at"]).date() == today
            ]
        plan_kcal = plan_response.data[0]["daily_kcal"]
        plan_proteine = plan_response.data[0]["daily_proteine"]
        plan_fiber = plan_response.data[0]["daily_fiber"]

        today_kcal = sum(m.get("energia_kcal", 0) or 0 for m in meals_today)
        today_prot = sum(m.get("proteina_gr", 0) or 0 for m in meals_today)
        today_raw_carb = sum(m.get("carbohidratos_gr", 0) or 0 for m in meals_today)
        today_fiber = sum(m.get("fibra_gr", 0) or 0 for m in meals_today)
        today_grasa = sum(m.get("grasas_gr", 0) or 0 for m in meals_today)

        today_kcal_pct = (today_kcal / plan_kcal * 100) if plan_kcal > 0 else 0
        today_prot_pct = (today_prot / plan_proteine * 100) if plan_proteine > 0 else 0
        today_fiber_pct = (today_fiber / plan_fiber * 100) if plan_fiber > 0 else 0

        today_kcal_left = plan_kcal - today_kcal
        today_prot_left = plan_proteine - today_prot
        today_fiber_left = round(plan_fiber - today_fiber)
        today_carb  = round(today_raw_carb - today_fiber ) # Carbohidratos netos
        
        # Procesar datos históricos por día
        daily_totals = {}
        for meal in meals_response.data:
            date = datetime.fromisoformat(meal["created_at"]).date()
            if date not in daily_totals:
                daily_totals[date] = {
                    "energia_kcal": 0,
                    "proteina_gr": 0,
                    "carbohidratos_gr": 0,
                    "fibra_gr": 0,
                    "grasas_gr": 0,
                }
            daily_totals[date]["energia_kcal"] += meal.get("energia_kcal", 0) or 0
            daily_totals[date]["proteina_gr"] += meal.get("proteina_gr", 0) or 0
            daily_totals[date]["carbohidratos_gr"] += meal.get("carbohidratos_gr", 0) or 0
            daily_totals[date]["fibra_gr"] += meal.get("fibra_gr", 0) or 0
            daily_totals[date]["grasas_gr"] += meal.get("grasas_gr", 0) or 0

        # Ordenar por fecha y obtener últimos 7 días
        sorted_dates = sorted(daily_totals.keys())
        last_7_days = sorted_dates[-7:] if len(sorted_dates) > 7 else sorted_dates
        last_15_days = sorted_dates[-15:] if len(sorted_dates) > 15 else sorted_dates

        # valores del plan
        dashboard_response.plan_kcal = plan_kcal
        dashboard_response.plan_proteine = plan_proteine
        dashboard_response.plan_fiber = plan_fiber

        # consumo de hoy
        dashboard_response.today_kcal = round(today_kcal)
        dashboard_response.today_proteine = round(today_prot)
        dashboard_response.today_carbohidratos = round(today_carb)
        dashboard_response.today_fiber = round(today_fiber)
        dashboard_response.today_grasa = round(today_grasa)
        # porcentajes
        dashboard_response.today_kcal_pct = round(today_kcal_pct)
        dashboard_response.today_prot_pct = round(today_prot_pct)
        dashboard_response.today_fiber_pct = round(today_fiber_pct)
        # lo que queda
        dashboard_response.today_kcal_left = round(today_kcal_left)
        dashboard_response.today_prot_left = round(today_prot_left)
        dashboard_response.today_fiber_left = round(today_fiber_left)
        
        dashboard_response.today_date = today  # Asumiendo que "today" es datetime
        dashboard_response.weekly_kcal = {
            date.strftime("%Y-%m-%d"): daily_totals[date]
            for date in last_15_days
        }

        # logger.info(f"Dashboard response: {dashboard_response}")

        return dashboard_response.model_dump()
        
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error generating dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching plans: {str(e)}")
