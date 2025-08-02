# Backend FastAPI - Dietik App

## Configuración Inicial

### 1. Instalar dependencias
```bash
# Desde la raíz del proyecto
pip install -r requirements.txt

# O desde la carpeta backend
cd backend
pip install -r ../requirements.txt
```

### 2. Configurar variables de entorno
Crea un archivo `.env` en la carpeta `backend/` con:

```env
SUPABASE_URL=https://<TU_PROJECTO>.supabase.co
SUPABASE_KEY=<TU_ANON_KEY>
SECRET_KEY=tu-secret-key-super-secreta-de-32-caracteres
```

**Para generar una SECRET_KEY segura:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 3. Configurar Supabase
1. Ve a tu [dashboard de Supabase](https://app.supabase.com/)
2. Crea un nuevo proyecto
3. Ve a Settings > API
4. Copia la URL y la anon key
5. Pégala en tu archivo `.env`

## Ejecutar el servidor

```bash
uvicorn main:app --reload
```

El servidor estará disponible en: http://localhost:8000

## Documentación automática

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing de Autenticación

### Opción 1: Script interactivo
```bash
python test_auth.py
```

### Opción 2: Usando curl

#### Registrar usuario:
```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "password123"}'
```

#### Login:
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "password123"}'
```

#### Probar ruta protegida:
```bash
curl -X GET "http://localhost:8000/api/user/profile" \
     -H "Authorization: Bearer TU_TOKEN_AQUI"
```

### Opción 3: Usando Swagger UI
1. Ve a http://localhost:8000/docs
2. Prueba los endpoints directamente desde la interfaz

## Endpoints disponibles

### Autenticación
- `POST /auth/register` - Registrar nuevo usuario
- `POST /auth/login` - Login de usuario
- `GET /api/user/profile` - Obtener perfil (protegido)

### Pruebas
- `GET /` - Verificar que el servidor esté funcionando

## Estructura del proyecto

```
backend/
├── main.py          # Aplicación principal FastAPI
├── auth.py          # Lógica de autenticación
├── models.py        # Modelos Pydantic
├── database.py      # Manager de base de datos
├── test_auth.py     # Script de pruebas
├── requirements.txt # Dependencias
└── README.md        # Este archivo
```

## Troubleshooting

### Error: "Module not found"
Asegúrate de estar en la carpeta `backend/` cuando ejecutes los comandos.

### Error: "Invalid credentials"
Verifica que las credenciales de Supabase en `.env` sean correctas.

### Error: "Connection refused"
Asegúrate de que el servidor esté corriendo con `uvicorn main:app --reload`

### Error: "Token expired"
Los tokens JWT expiran después de 30 minutos por defecto. Vuelve a hacer login. 