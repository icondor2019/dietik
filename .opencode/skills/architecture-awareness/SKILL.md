---
name: architecture-awareness
description: Provides guidelines and documentation for architecture decisions
---

# Architecture Awareness

This skill defines the high-level architecture, tech stack, and constraints for the Dietik App project.

---

## Project Overview

Dietik App is a nutritional tracking system that processes:
- User meal tracking
- Nutritional plans
- Body measurements
- Food descriptions
- Product database for calorie calculations

---

## Tech Stack

### Backend
- **FastAPI** - REST API server
- **Python** - Core language
- **LangChain/LangGraph** - Agentic workflow orchestration (replaces n8n)

### Database & Auth
- **Supabase** - PostgreSQL database + JWT authentication

### AI Services
- **OpenAI** - Embeddings and text generation
- **Groq Whisper** - Audio transcription

### Frontend
- **Static HTML/CSS/JS** - Minimal web UI with Bootstrap

### Integrations
- **Telegram** - Webhook-based user input ingestion

---

## Architecture

### Layer Separation

```
frontend/          → Static HTML/JS UI
backend/           → FastAPI REST API + controllers
agentic_service/   → LangChain/LangGraph workflows
configuration/     → Centralized settings (Pydantic)
```

### Data Flow

1. **Input**: Telegram webhook or frontend → FastAPI controllers
2. **Processing**: Agentic workflows (LangGraph) handle complex logic
3. **Storage**: Supabase (PostgreSQL) for persistence
4. **AI Services**: OpenAI (embeddings/text), Groq (audio transcription)

### Key Domains

- **Meals** - User meal tracking
- **Plans** - Nutritional plans
- **Body Dimensions** - Weight, measurements
- **Products** - Food database for calorie calculations
- **Authentication** - JWT-based auth via Supabase

---

## Constraints

- Ignore files prefixed with `local_`
- Use controller pattern for API endpoints (see `fastapi-controller-pattern` skill)
- Centralize configuration via `configuration/settings.py` (see `configuration-management` skill)
- Agentic workflows replace n8n logic
- Follow FastAPI structure (see `fastapi-structure` skill)

---

## Rules

- Keep backend and frontend separated
- Agentic workflows must be in `agentic_service/`
- All AI/LLM logic goes through LangChain/LangGraph
- Database operations go through Supabase client
- No direct environment variable access (use `configuration/settings.py`)
