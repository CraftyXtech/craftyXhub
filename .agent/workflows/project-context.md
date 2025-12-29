---
description: Project context for CraftyXHub frontend - READ THIS FIRST in every new chat
---

# CraftyXHub Project Context

## Overview

CraftyXHub is a modern blogging and content management platform featuring a public-facing blog and a comprehensive dashboard for content creators and administrators. It leverages AI for content assistance and includes robust authentication and media management.

## Tech Stack

### Frontend

- **Framework**: React 19 + Vite 7
- **UI Library**: Material UI (MUI) v7
- **Styling**: Emotion, tailwindcss (implied), Framer Motion (animations)
- **Data Fetching**: Axios, SWR
- **Routing**: React Router v7
- **Editors**: EditorJS, TinyMCE

### Backend

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (AsyncPG), SQLModel (ORM), Alembic (Migrations)
- **Authentication**: JWT, FastAPI-SSO
- **AI Integration**: OpenAI, Google Generative AI (Gemini), Pydantic AI
- **Caching**: Redis

## Key Directories

### Frontend (`frontend/src`)

- **`views/public`**: Public pages (Home, Blog, Post Details, etc.)
- **`views/dashboard`**: Admin and User Dashboard (Posts, Media, Profile, Settings)
- **`api`**: Centralized API service layer
- **`layouts`**: `DashboardLayout`, `PublicLayout`, `AuthLayout`
- **`components`**: Reusable UI components

### Backend (`api`)

- **`routers/v1`**: API endpoints (Auth, Posts, Users, AI, Comments, etc.)
- **`models`**: Database models (SQLModel)
- **`services`**: Business logic layers
- **`database`**: DB connection and session management

## Development Commands

### Backend

Run in `api/` directory:

```bash
uvicorn main:app --reload
```

or via VS Code launch configurations if available.

### Frontend

Run in `frontend/` directory:

```bash
npm run dev
```

## Workflows

- Check `.agent/workflows` for other specific guides.
- **Project Structure**: Monorepo-style with `api` and `frontend` separation.
