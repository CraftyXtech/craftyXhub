# CraftyXhub Backend ➜ FastAPI Migration Guide

This document enumerates **every Laravel backend component** currently implemented in the CraftyXhub project.  Use this as the authoritative checklist for porting functionality to FastAPI.

> **Scope**  
> • *Backend only* – Front-end (React / Inertia) assets and the `demo1` / `Litho` examples are **not** covered here.  
> • *One-to-one mapping* – Each PHP file listed below requires an equivalent FastAPI (Python) implementation.

---

## 1. Artisan Console Commands
Migrates to FastAPI CLI scripts (e.g. [Typer](https://typer.tiangolo.com/)) or management tasks.

| File | Purpose |
| --- | --- |
| `app/Console/Commands/GeneratePostEmbeddings.php` | Calculates vector embeddings for posts. |
| `app/Console/Commands/SeedUserReadsAndTopics.php` | Seeds user-read and topic-interest data. |

## 2. HTTP Controllers → FastAPI Routers
Each controller becomes one or more FastAPI *router* modules (`@router.get`, `@router.post`, etc.).

### 2.1 Admin Controllers
- `app/Http/Controllers/Admin/AdminDashboardController.php`
- `app/Http/Controllers/Admin/AdminPostController.php`
- `app/Http/Controllers/Admin/AdminSettingsController.php`
- `app/Http/Controllers/Admin/AdminSystemController.php`

### 2.2 API Controllers
- `app/Http/Controllers/Api/AiController.php`
- `app/Http/Controllers/Api/CommentController.php`
- `app/Http/Controllers/Api/InteractionController.php`
- `app/Http/Controllers/Api/PostController.php`
- `app/Http/Controllers/Api/RecommendationController.php`
- `app/Http/Controllers/Api/SearchController.php`
- `app/Http/Controllers/Api/UserPersonalizationController.php`
- `app/Http/Controllers/Api/UserProfileController.php`

### 2.3 Auth Controllers
- `app/Http/Controllers/Auth/AuthenticatedSessionController.php`
- `app/Http/Controllers/Auth/ConfirmablePasswordController.php`
- `app/Http/Controllers/Auth/EmailVerificationNotificationController.php`
- `app/Http/Controllers/Auth/EmailVerificationPromptController.php`
- `app/Http/Controllers/Auth/NewPasswordController.php`
- `app/Http/Controllers/Auth/PasswordController.php`
- `app/Http/Controllers/Auth/PasswordResetLinkController.php`
- `app/Http/Controllers/Auth/RegisteredUserController.php`
- `app/Http/Controllers/Auth/VerifyEmailController.php`

### 2.4 Editor-Side Controllers
- `app/Http/Controllers/Editor/CategoryController.php`
- `app/Http/Controllers/Editor/EditorDashboardController.php`
- `app/Http/Controllers/Editor/PostController.php`
- `app/Http/Controllers/Editor/TagController.php`

### 2.5 Public Web Controllers
- `app/Http/Controllers/Web/CommentController.php`
- `app/Http/Controllers/Web/InteractionController.php`
- `app/Http/Controllers/Web/PostController.php`
- `app/Http/Controllers/Web/UserProfileController.php`

### 2.6 Misc. Root Controllers
*(Small placeholder stubs ‑ validate necessity before porting)*
- `app/Http/Controllers/BookmarkController.php`
- `app/Http/Controllers/CategoryController.php`
- `app/Http/Controllers/CommentController.php`
- `app/Http/Controllers/Controller.php`
- `app/Http/Controllers/FolllowController.php`
- `app/Http/Controllers/LikeController.php`
- `app/Http/Controllers/MediaController.php`
- `app/Http/Controllers/PostController.php`
- `app/Http/Controllers/ProfileController.php`
- `app/Http/Controllers/TagController.php`
- `app/Http/Controllers/ViewController.php`

## 3. Middleware
Convert to FastAPI **dependency** or **middleware** classes.
- `app/Http/Middleware/HandleInertiaRequests.php`
- `app/Http/Middleware/EnsureUserIsAdmin.php`
- `app/Http/Middleware/EnsureUserIsEditor.php`

## 4. Form Requests / Validators → Pydantic Models + Depends
- `app/Http/Requests/ProfileUpdateRequest.php`
- `app/Http/Requests/Auth/LoginRequest.php`

## 5. API Resources → Response Schemas
Laravel resources serialize models; migrate to **Pydantic** response models.
- `app/Http/Resources/CommentResource.php`
- `app/Http/Resources/PostResource.php`
- `app/Http/Resources/TagResource.php`
- `app/Http/Resources/UserProfileResource.php`

## 6. Eloquent Models → SQLModel / SQLAlchemy Models
Every model below needs a Python ORM equivalent plus Alembic migration.

```
app/Models/
├── Bookmark.php
├── Category.php
├── Comment.php
├── Like.php
├── Media.php
├── Post.php
├── Tag.php
├── User.php
├── UserPreference.php
├── UserRead.php
├── UserTopic.php
├── View.php
└── Folllow.php
```

## 7. Domain Services
Re-implement as injectable service classes / utils.

```
app/Services/
├── Admin/
│   ├── ContentManagementService.php
│   └── UserManagementService.php
├── Editor/
│   └── PostManagementService.php
├── EmbeddingService.php
├── ImageGenerationService.php
└── RecommendationService.php
```

## 8. Observers → SQLAlchemy Event Listeners / Custom Hooks
- `app/Observers/PostObserver.php`

## 9. Authorization Policies → FastAPI Role-Based Access
- `app/Policies/PostPolicy.php`

## 10. Providers → Dependency Injection Setup
- `app/Providers/AppServiceProvider.php`
- `app/Providers/AuthServiceProvider.php`

## 11. Routes
Map to FastAPI `APIRouter`s and include appropriate auth dependencies.
- `routes/web.php`
- `routes/auth.php`
- `routes/console.php` *(CLI only)*

## 12. Configuration
All files in `config/*.php` must have their settings ported to a new Python-based configuration management system (e.g., Pydantic's `BaseSettings` with a `.env` file). This includes, but is not limited to:
- `config/app.php` (App name, environment, timezone, etc.)
- `config/auth.php` (Authentication guards and providers)
- `config/database.php` (Database connections)
- `config/filesystems.php` (Storage disks)
- `config/hashing.php`
- `config/logging.php`
- `config/mail.php`
- `config/queue.php`
- `config/services.php` (Third-party service credentials)
- `config/session.php`

## 13. Database Layer
### 12.1 Migrations (Eloquent ➜ Alembic)
All `database/migrations/*.php` files (23 total) create or alter tables; port each to Alembic revision scripts.

### 12.2 Seeders & Factories → Fixtures / Initializers
- `database/seeders/*.php` (6 files)
- `database/factories/*.php` (4 files)

## 14. Automated Tests
Laravel **Pest** / PHPUnit tests live under `tests/`.  Re-write using **Pytest** once routes & models are migrated. This includes:
- `tests/Feature/`
- `tests/Unit/`

## 15. Service Container & Bootstrapping
Logic from `bootstrap/app.php` and `bootstrap/providers.php` may need to be replicated in FastAPI's startup events or dependency injection system.

## 16. Core Application Entrypoint
- **`public/index.php`**: This is the main entrypoint for all HTTP requests in the Laravel application. Its equivalent in the new project will be the Python script that initializes the FastAPI app instance and is run by an ASGI server like Uvicorn.

## 17. Dependencies
The `composer.json` file lists all PHP dependencies. Each one must be evaluated and replaced with a suitable Python equivalent.

---

### Next Steps Checklist
1. Set up FastAPI project skeleton (`app`, `routers`, `schemas`, `models`, etc.).
2. Implement authentication (JWT / OAuth) to mirror Laravel’s session & token logic.
3. Create SQLAlchemy models and Alembic migrations matching Eloquent schema.
4. Port services, then controllers → routers.
5. Integrate middleware, dependencies, and response models.
6. Reproduce console commands with Typer scripts.
7. Re-create tests in Pytest.

> **Tip:** Migrate incrementally (model → route → service) and ensure parity with existing PHPUnit tests to maintain feature fidelity. 