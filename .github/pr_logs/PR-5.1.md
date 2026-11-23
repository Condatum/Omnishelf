## Pull Request: [PR-5.1] [FEAT] Contextual Resumption Viewport & Deep-Link Launcher
**Source Branch:** `feat/5.1-sandboxed-viewport-reader` -> **Target Branch:** `main`

### 1. Objective & Scope Alignment
- **OmniShelf Objective Addressed:** Contextual Resumption & Zero-Friction Deep-Link Launching
- **Micro-Task Summary:** Built `ViewportReaderView` (`/reader/<uuid:entry_id>/`), wired every Grand Library card's primary **Deep-Link Resume** CTA directly to the sandboxed viewport, implemented automatic `last_read_at` session timestamp tracking, and created a distraction-free Reader HUD with context notes reveal and an instant **External Tab Fallback** detector for `X-Frame-Options` / anti-bot sites.

### 2. Technical Changes
- **Models/Migrations:** None (updates `LibraryEntry.last_read_at` atomically on session launch).
- **Views/URLs/HTMX Endpoints:** Implemented `ViewportReaderView` in `reader/views.py`, created `reader/urls.py` (`reader:viewport`), and mounted `/reader/` in `omnishelf_core/urls.py`.
- **Templates/UI (`modern-web-guidance`):** Created `templates/reader/viewport.html` with accessible `role="toolbar"` HUD controls, descriptive `<iframe title="..." sandbox="allow-scripts allow-same-origin allow-forms allow-popups">`, reload control, context notes reveal, and X-Frame fallback banner; updated `templates/library/partials/entry_card.html` Deep-Link Resume CTA.

### 3. Guardrail & Limitation Checklist
- [x] Zero story text/image scraping, proxy stripping, or copyright caching introduced.
- [x] Strict `request.user` tenancy isolation enforced on all queries.
- [x] All unit tests pass (`python manage.py test` — 29 tests OK).
