from fastapi import APIRouter, HTTPException, Depends
from backend.auth import create_access_token, authenticate_user, register_user
from backend.models import UserLogin, Token, UserRegister

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    try:
        # Autenticar con Supabase
        user = await authenticate_user(user_credentials.email, user_credentials.password)
        
        if user:
            # Crear JWT token
            access_token = create_access_token(
                data={"sub": user.id, "email": user.email}
            )
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")


@router.post("/register")
async def register(user_credentials: UserRegister):
    try:
        # Registrar usuario en Supabase
        user = await register_user(user_credentials.email, user_credentials.password,
                                   user_credentials.telegram_id, user_credentials.name)

        if user:
            return {"message": "User registered successfully", "user_id": user.id}
        else:
            raise HTTPException(status_code=400, detail="Registration failed")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail="Registration failed")
