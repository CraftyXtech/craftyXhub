---
description: Project context for CraftyXHub frontend - READ THIS FIRST in every new chat
---

# 🚨 CraftyXHub Project Context

> **IMPORTANT**: Read this before making any changes!

---

## 📁 Folder Roles (CRITICAL)

| Folder     | Role                  | What To Do                        |
| ---------- | --------------------- | --------------------------------- |
| **litho/** | ⚠️ OLD template       | Migrating FROM - reference only   |
| **admin/** | ⚠️ OLD dashboard      | Migrating FROM - reference only   |
| **uikit/** | 📐 Design inspiration | Use for public pages texture/feel |
| **vite/**  | 📐 Design inspiration | Use for dashboard UI patterns     |
| **src/**   | ✅ NEW unified app    | **ALL new code goes here!**       |

---

## 🎯 What We're Doing

**Creating a premium unified website** by:

1. Migrating blog features from `litho/` → `src/views/public/`
2. Migrating dashboard from `admin/` → `src/views/dashboard/`
3. Using `uikit/` aesthetics for public pages
4. Using `vite/` patterns for dashboard design

---

## 🎨 Design Standards

- **Font**: Open Sans ✅ (done)
- **UI**: MUI v5
- **Styling**: Theme tokens only (no hardcoded colors)
- **Goal**: Premium, modern, polished look

---

## 📂 Target Structure (src/)

```
src/
├── components/        # Shared components
├── views/
│   ├── public/        # Blog, Home, About, Contact
│   └── dashboard/     # Admin pages
├── layouts/           # PublicLayout, DashboardLayout
├── themes/            # MUI theme config
└── services/          # API layer
```

---

## ✅ Progress

- [x] Open Sans font
- [x] Base theme setup
- [ ] Public page polish
- [ ] Dashboard migration
- [ ] Color refinement

---

## 🚀 Commands

```bash
npm run dev    # Dev server
npm run build  # Build
```
