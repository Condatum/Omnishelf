## Pull Request: [PR-0.2] [FEAT] Unified Base Template & Low-Friction UI Shell
**Source Branch:** `feat/0.2-base-ui-shell` -> **Target Branch:** `main`

### 1. Objective & Scope Alignment
- **OmniShelf Objective Addressed:** UI Fatigue Prevention / Calm Dark-Mode Design System
- **Micro-Task Summary:** Implemented `templates/base.html` with dark-mode `color-scheme` meta/root styling, Tailwind CSS, HTMX 2.0 (with CSRF header injection), Alpine.js 3.x, responsive mobile/desktop navigation, skip-to-content accessibility link, and live toast notification region. Added root `home_view` and landing shell.

### 2. Technical Changes
- **Models/Migrations:** None.
- **Views/URLs/HTMX Endpoints:** `library/views.py` (`home_view`), `accounts/urls.py` (placeholder routes for nav resolution), `omnishelf_core/urls.py`.
- **Templates/UI (`modern-web-guidance`):** `templates/base.html`, `templates/library/home.html`.

### 3. Guardrail & Limitation Checklist
- [x] Zero story text/image scraping or copyright caching introduced.
- [x] Strict `request.user` tenancy isolation enforced on all queries.
- [x] All unit tests pass (`python manage.py test`).

