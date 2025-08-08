from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from supabase import create_client, Client
import sys
import os
from loguru import logger

# Agregar el directorio raíz al path para importar settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from configuration.settings import (
    SECRET_KEY, 
    ALGORITHM, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SUPABASE_URL,
    SUPABASE_KEY
)

# Importar models desde el directorio backend
from .models import UserLogin, Token

# Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Security
security = HTTPBearer()

def create_access_token(data: dict):
    """Crear token JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verificar token JWT y retornar user_id"""
    try:
        print(f"Verifying token: {credentials.credentials[:20]}...")
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            print("Token payload missing 'sub' field")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        print(f"Token verified successfully for user_id: {user_id}")
        return user_id
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError as e:
        print(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def authenticate_user(email: str, password: str):
    """Autenticar usuario con Supabase"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            return response.user
        return None
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

async def register_user(email: str, password: str, telegram_id: int, name: str = None):
    logger.info(f"Registering user with email: {email} and telegram_id: {telegram_id}")
    """Registrar nuevo usuario en Supabase"""
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user:
            # Crear perfil de usuario en la tabla users
            await create_user_profile(response.user.id, telegram_id, name)
            return response.user
        return None
    except Exception as e:
        print(f"Registration error: {e}")
        return None

def get_current_user(user_id: str = Depends(verify_token)):
    """Obtener usuario actual desde Supabase usando el token"""
    try:
        user_data = supabase.auth.get_user(user_id)
        return user_data.user
    except Exception as e:
        logger.error(f"Error fetching user data: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

async def create_user_profile(user_id: str, telegram_id: int,  name: str = None):
    """Crear perfil de usuario en la tabla clients de Supabase"""
    try:
        # Preparar los datos del usuario
        user_data = {
            "supabase_user_uuid": user_id,
            "name": name,
            "telegram_id": telegram_id
        }

        # Insertar en la tabla clients
        response = supabase.table("clients").insert(user_data).execute()
        
        if response.data:
            print(f"User profile created successfully: {user_id}")
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user profile"
            )
    except Exception as e:
        print(f"Error creating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

async def create_default_plan(telegram_id: int):
    """Crear perfil de usuario en la tabla clients de Supabase"""
    try:
        # Preparar los datos del usuario
        data = {
            "client_id": telegram_id,
            "daily_kcal": 1800,
            "daily_proteine": 120,
            "daily_carbohydrates": 120,
            "status": "active"
        }

        # Insertar en la tabla clients
        response = supabase.table("plans").insert(data).execute()
        
        if response.data:
            print(f"Default Nutritional plan created successfully: {telegram_id}")
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user deafault plan"
            )
    except Exception as e:
        print(f"Error creating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
