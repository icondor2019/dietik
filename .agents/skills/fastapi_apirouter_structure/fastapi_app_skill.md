---
name: FastAPI APIRouter Project Structure
description: How to structure a FastAPI project using APIRouter controllers with a centralized aggregator pattern
---

# FastAPI APIRouter Project Structure

This skill defines how to structure a FastAPI backend using the **APIRouter controller pattern**: each group of related endpoints lives in its own controller file, and a central `__init__.py` aggregates all routers into a single `api_router` that `main.py` includes.

## Project Structure

```
project_root/
├── main.py                          # App creation, middleware, lifespan, include_router
├── configuration/
│   └── settings.py                  # All env vars and config constants
├── backend/
│   ├── __init__.py
│   ├── auth.py                      # Auth utilities (JWT, token verification)
│   ├── models.py                    # Pydantic models
│   ├── controllers/                 # All endpoint controllers
│   │   ├── __init__.py              # Aggregates all routers → exports api_router
│   │   ├── health_controller.py     # Health check endpoints
│   │   ├── authentication_controller.py
│   │   ├── user_controller.py
│   │   └── <domain>_controller.py   # One file per domain/feature
│   ├── responses/                   # Response models
│   └── utils/                       # Shared utilities
├── tests/
│   └── test_endpoints.py            # Smoke tests using FastAPI TestClient
└── requirements.txt
```

## Step-by-step Guide

### 1. Create a Controller File

Each controller file defines a `router` with a prefix and tag. All endpoints use `@router` instead of `@app`.

```python
# backend/controllers/example_controller.py
from fastapi import APIRouter, HTTPException, Depends

router = APIRouter(prefix="/api/example", tags=["Example"])


@router.get("")
async def list_items():
    return {"data": []}


@router.post("")
async def create_item(item: dict):
    return {"message": "Created", "data": item}


@router.delete("/{item_id}")
async def delete_item(item_id: str):
    return {"message": "Deleted"}
```

**Rules:**
- File name: `<domain>_controller.py` (e.g. `meals_controller.py`, `auth_controller.py`)
- Always export `router = APIRouter(prefix="...", tags=["..."])`
- The `prefix` + individual route paths must produce the final URL (e.g. prefix `/api/meals` + route `/create` = `/api/meals/create`)
- Use `tags` for OpenAPI docs grouping
- Import dependencies (auth, models, settings) at the top — **do not** import `app`

### 2. Always Include a Health Controller

Every project should have a health check endpoint for monitoring:

```python
# backend/controllers/health_controller.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("")
async def health_check():
    """Simple endpoint to check if the app is running."""
    return {"status": "healthy", "message": "App is running"}
```

### 3. Create the Controllers `__init__.py`

This file aggregates all individual routers into a single `api_router`:

```python
# backend/controllers/__init__.py
from fastapi import APIRouter
from backend.controllers.health_controller import router as health_router
from backend.controllers.authentication_controller import router as auth_router
from backend.controllers.example_controller import router as example_router
# ... import all other controllers

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(example_router)
# ... include all other routers
```

**Rules:**
- Import each controller's `router` with an alias (`as xxx_router`)
- Create one `api_router = APIRouter()` and include all sub-routers
- This is the **only** export that `main.py` needs

### 4. Set Up `main.py`

`main.py` should only handle app creation, middleware, and router inclusion — **no endpoint definitions**:

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from contextlib import asynccontextmanager

from configuration.settings import APP_NAME, APP_VERSION, HOST, PORT
from backend.controllers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting app...")
    yield
    logger.info("Closing app...")


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan
)

# Middleware setup (CORS, etc.)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def setup_application():
    app.include_router(api_router)


setup_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
```

### 5. Add Smoke Tests

Create endpoint tests using FastAPI's `TestClient` (no running server needed):

```python
# tests/test_endpoints.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoints:
    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestProtectedEndpointsRequireAuth:
    @pytest.mark.parametrize("method,path", [
        ("GET", "/api/user/profile"),
        # ... add all protected endpoints
    ])
    def test_protected_returns_401(self, method, path):
        response = client.request(method, path)
        assert response.status_code in (401, 403)
```

Run with:
```bash
python -m pytest tests/ -v
```

**Testing dependencies** (add to `requirements.txt`):
```
pytest>=8.0.0
httpx>=0.27.0
```

## Grouping Guidelines

When deciding how to group endpoints into controllers:

| Guideline | Example |
|---|---|
| Group by **domain entity** | All `/api/meals/*` → `meals_controller.py` |
| Separate entities that may grow independently | Products search → `products_controller.py` even if only 1 endpoint |
| Keep auth endpoints together | login + register → `authentication_controller.py` |
| Dashboard/analytics get their own controller | `dashboard_controller.py` |
| General/utility endpoints (health, config, test) | `general_controller.py` or `health_controller.py` |

## Adding a New Controller Checklist

1. Create `backend/controllers/<domain>_controller.py` with `router = APIRouter(prefix="...", tags=["..."])`
2. Add endpoints using `@router.get(...)`, `@router.post(...)`, etc.
3. Import and include the router in `backend/controllers/__init__.py`
4. Add smoke tests in `tests/test_endpoints.py`
5. No changes needed in `main.py`
