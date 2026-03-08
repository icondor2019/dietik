# Dietik App

Aplicación web para el seguimiento de actividad física y nutricional.

## System design
![img alt](https://github.com/icondor2019/dietik/blob/main/dietik_app_system.jpg?raw=true)

## Configuración de Variables de Entorno

### 1. Crear archivo .env

Copia el archivo `env.example` a `.env` y configura las variables necesarias:

```bash
cp env.example .env
```

### 2. Variables Requeridas

Edita el archivo `.env` y configura las siguientes variables **obligatorias**:

```env
# Configuración de Supabase (REQUERIDO)
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Configuración de JWT (REQUERIDO)
SECRET_KEY=your-secret-key-change-in-production
```

### 3. Variables Opcionales

Las siguientes variables tienen valores por defecto pero puedes personalizarlas:

```env
# Configuración de la aplicación
DEBUG=False

# Configuración del servidor
HOST=0.0.0.0
PORT=8000

# Configuración de JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración CORS
CORS_ORIGINS=*
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

# Configuración del frontend
FRONTEND_URL=http://localhost:3000
API_BASE_URL=http://localhost:8000

# Configuración de logging
LOG_LEVEL=INFO
LOG_FILE=app.log
```

## Instalación

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar variables de entorno** (ver sección anterior)

3. **Ejecutar el backend:**
   ```bash
   cd backend
   python main.py
   ```

4. **Abrir el frontend:**
   - Abre `frontend/login.html` en tu navegador
   - O sirve los archivos estáticos con un servidor web

## Estructura del Proyecto

```
dietik_app/
├── backend/                 # Backend en FastAPI
│   ├── main.py             # Servidor principal
│   ├── auth.py             # Autenticación y JWT
│   ├── models.py           # Modelos de datos
│   └── database.py         # Configuración de base de datos
├── configuration/          # Configuración centralizada
│   └── settings.py         # Variables de entorno
├── frontend/              # Frontend en HTML/JS
│   ├── login.html         # Página de login/registro
│   └── daily_activity.html # Página principal
├── requirements.txt       # Dependencias de Python
├── env.example           # Ejemplo de variables de entorno
└── README.md            # Este archivo
```

## Características

- **Autenticación JWT** con Supabase
- **Registro de actividad diaria** (peso, grasa, músculo, hambre, ejercicio)
- **Historial de actividades** agrupado por día
- **Configuración centralizada** de variables de entorno
- **Frontend responsive** con Bootstrap
- **API RESTful** con FastAPI

## Desarrollo

### Backend

El backend está construido con FastAPI y utiliza:
- **Supabase** para autenticación y base de datos
- **JWT** para tokens de autenticación
- **CORS** configurado para permitir requests del frontend
- **Variables de entorno** centralizadas en `configuration/settings.py`

### Frontend

El frontend es una aplicación web estática que:
- Carga la configuración dinámicamente desde el backend
- Maneja autenticación con JWT
- Permite registro de actividades diarias
- Muestra historial de actividades

## Seguridad

- Las variables sensibles se manejan a través de variables de entorno
- Los tokens JWT tienen tiempo de expiración configurable
- CORS está configurado para controlar el acceso desde el frontend
- Las credenciales de Supabase se validan al inicio de la aplicación

## Troubleshooting

### Error de configuración

Si ves el error "Las siguientes variables de entorno son requeridas", asegúrate de:
1. Haber creado el archivo `.env`
2. Haber configurado `SUPABASE_URL`, `SUPABASE_KEY` y `SECRET_KEY`
3. Que el archivo `.env` esté en el directorio raíz del proyecto

### Error de conexión con Supabase

Verifica que:
1. Las credenciales de Supabase sean correctas
2. La URL y la clave anónima estén bien configuradas
3. El proyecto de Supabase esté activo

## Testing

### Dependencias

Las dependencias de testing (`pytest`, `httpx`) ya están incluidas en `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Ejecutar los tests

Desde la raíz del proyecto:

```bash
# Ejecutar todos los tests
python -m pytest tests/ -v

# Ejecutar solo los tests de endpoints
python -m pytest tests/test_endpoints.py -v
```

### Qué se testea

- **Endpoints públicos**: verifica que `/api/health`, `/api`, `/api/test` y `/api/config` responden correctamente
- **Endpoints protegidos**: verifica que los endpoints que requieren autenticación rechazan peticiones sin token (401/403)
