## Pull Request: [PR-2.2] [FEAT] LibraryEntry & ReadingSnapshot Persistence Schema
**Source Branch:** `feat/2.2-library-and-snapshot-models` -> **Target Branch:** `main`

### 1. Objective & Scope Alignment
- **OmniShelf Objective Addressed:** Reading State Persistence & Source Volatility Protection
- **Micro-Task Summary:** Implemented `LibraryEntry` (with custom title/cover overrides, active Deep-Link URI, automatic `source_domain` extraction, folder/tag relations, and context notes) and `ReadingSnapshot` (immutable URI audit history per entry).

### 2. Technical Changes
- **Models/Migrations:** `library/models.py` (`LibraryEntry`, `ReadingSnapshot`), `library/migrations/0002_libraryentry_readingsnapshot.py`, `library/admin.py`.
- **Views/URLs/HTMX Endpoints:** None.
- **Templates/UI (`modern-web-guidance`):** None.

### 3. Guardrail & Limitation Checklist
- [x] Zero story text/image scraping or copyright caching introduced.
- [x] Strict `request.user` tenancy isolation enforced on all queries.
- [x] All unit tests pass (`python manage.py test` — 15 tests OK).

