## Pull Request: [PR-3.1] [FEAT] The "Grand Library" Dashboard & Visual Card Grid
**Source Branch:** `feat/3.1-grand-library-grid` -> **Target Branch:** `main`

### 1. Objective & Scope Alignment
- **OmniShelf Objective Addressed:** Visual Reading Dashboard & Low-Friction Interface
- **Micro-Task Summary:** Built `GrandLibraryView` scoped strictly to `request.user`, wired `/library/` and authenticated `/` routing, and designed the responsive dark-mode visual card grid with cover fallbacks, status badges, chapter pills, source domain badges, and primary Deep-Link Resume / Update Snapshot actions following `modern-web-guidance`.

### 2. Technical Changes
- **Models/Migrations:** Added read-only presentation properties (`cover_src`, `fallback_gradient`, `status_badge_classes`) to `LibraryEntry` in `library/models.py` (no schema migrations required).
- **Views/URLs/HTMX Endpoints:** Implemented `GrandLibraryView` and updated `home_view` in `library/views.py`; created `library/urls.py` (`library:dashboard`) and included it in `omnishelf_core/urls.py`.
- **Templates/UI (`modern-web-guidance`):** Updated `templates/base.html` with intrinsic CSS grid (`repeat(auto-fill, minmax(...))`), container query contexts, `:focus-visible` outlines, and modal `<dialog>` containment; created `templates/library/dashboard.html`, `templates/library/partials/entry_grid.html`, and `templates/library/partials/entry_card.html`.

### 3. Guardrail & Limitation Checklist
- [x] Zero story text/image scraping or copyright caching introduced.
- [x] Strict `request.user` tenancy isolation enforced on all queries.
- [x] All unit tests pass (`python manage.py test` — 18 tests OK).
