## Pull Request: [PR-2.1] [FEAT] Multi-Tier Taxonomy Models (Folders, Tags, Statuses)
**Source Branch:** `feat/2.1-taxonomy-models` -> **Target Branch:** `main`

### 1. Objective & Scope Alignment
- **OmniShelf Objective Addressed:** Flexible Taxonomy & Multi-Tier Organization
- **Micro-Task Summary:** Defined `ReadingStatus` TextChoices (`ACTIVE`, `ON_HOLD`, `BINGE_READY`, `HIATUS`, `COMPLETED`), user-scoped `Folder` model, and user-scoped `Tag` model with automatic slugification and per-user uniqueness constraints.

### 2. Technical Changes
- **Models/Migrations:** `library/models.py` (`ReadingStatus`, `Folder`, `Tag`), `library/migrations/0001_initial.py`, `library/admin.py`.
- **Views/URLs/HTMX Endpoints:** None.
- **Templates/UI (`modern-web-guidance`):** None.

### 3. Guardrail & Limitation Checklist
- [x] Zero story text/image scraping or copyright caching introduced.
- [x] Strict `request.user` tenancy isolation enforced on all queries.
- [x] All unit tests pass (`python manage.py test` — 12 tests OK).

