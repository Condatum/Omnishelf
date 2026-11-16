## Pull Request: [PR-1.2] [FEAT] Data Sovereignty Portable Backup & Sync Engine
**Source Branch:** `feat/1.2-data-sovereignty-sync` -> **Target Branch:** `main`

### 1. Objective & Scope Alignment
- **OmniShelf Objective Addressed:** Data Sovereignty & Cloud-Ready Portability
- **Micro-Task Summary:** Added JSON library export and idempotent import endpoints (`accounts/backup.py`, `accounts/views.py`, `accounts/urls.py`) and an Account & Data Sovereignty UI (`templates/accounts/settings.html`).

### 2. Technical Changes
- **Models/Migrations:** None (uses dynamic `apps.get_model` lookup for `Folder`, `Tag`, `LibraryEntry`, `ReadingSnapshot`).
- **Views/URLs/HTMX Endpoints:** `/accounts/settings/`, `/accounts/export/`, `/accounts/import/`.
- **Templates/UI (`modern-web-guidance`):** `templates/accounts/settings.html`, updated `templates/base.html` navigation.

### 3. Guardrail & Limitation Checklist
- [x] Zero story text/image scraping or copyright caching introduced.
- [x] Strict `request.user` tenancy isolation enforced on all queries.
- [x] All unit tests pass (`python manage.py test` — 9 tests OK).

